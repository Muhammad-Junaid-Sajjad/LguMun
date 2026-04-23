import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Committee, Delegate, AdminQuery, SystemSettings
from app.schemas import DelegateCreate, CommitteeResponse, AdminQueryCreate, AdminQueryResponse, QueryReply, QueryStatusUpdate, SystemSettingCreate, SystemSettingResponse, AdminStats
from app.exceptions import AppException
from app.constants import ROLL_NUMBER_PREFIX, ROLL_NUMBER_DIGITS, MAX_TRANSFERS, ADMIN_API_KEY_HEADER

logger = logging.getLogger(__name__)

def _committee_to_response(c: Committee) -> dict:
    return {
        "id": c.id,
        "short_name": c.short_name,
        "full_name": c.full_name,
        "chair_name": c.chair_name or "To be announced",
        "agenda_1": c.agenda_1 or "To be announced",
        "agenda_2": c.agenda_2,
        "total_seats": c.total_seats,
        "filled_seats": c.filled_seats,
        "language": c.language,
        "contact_info": c.contact_info,
        "is_full": c.filled_seats >= c.total_seats,
        "capacity_percentage": int((c.filled_seats / c.total_seats) * 100) if c.total_seats > 0 else 100,
    }

def get_all_committees(db: Session) -> list[dict]:
    committees = db.query(Committee).filter(Committee.is_active == True).all()
    return [_committee_to_response(c) for c in committees]

def get_committee_by_id(db: Session, committee_id: int) -> dict | None:
    c = db.query(Committee).filter(
        Committee.id == committee_id,
        Committee.is_active == True
    ).first()
    return _committee_to_response(c) if c else None

def register_delegate(db: Session, data: DelegateCreate, ip: str) -> dict:
    try:
        # Step 0 — Check if ALL committees are full
        all_committees = db.query(Committee).filter(Committee.is_active == True).all()
        all_full = all(c.filled_seats >= c.total_seats for c in all_committees)
        if all_full:
            raise AppException(
                "ALL_COMMITTEES_FULL",
                "All committees are now full. Please contact LGUMUN Society Core Team.",
                field="committee_id",
                status_code=409
            )

        # Step 1 — Duplicate email check (case-insensitive already lowercased by schema)
        existing = db.query(Delegate).filter(Delegate.email == data.email).first()
        if existing:
            # Check if this delegate can still transfer
            can_transfer = existing.transfer_count < MAX_TRANSFERS
            transfers_left = MAX_TRANSFERS - existing.transfer_count

            existing_data = {
                "roll_number": existing.roll_number,
                "full_name": existing.full_name,
                "committee": existing.committee.short_name if existing.committee else "N/A",
                "committee_full": existing.committee.full_name if existing.committee else "N/A",
                "transfer_count": existing.transfer_count,
                "can_transfer": can_transfer,
                "transfers_left": transfers_left,
                "is_final": not can_transfer,
                "final_committee": existing.committee.short_name,
                "final_roll_number": existing.roll_number
            }

            if can_transfer:
                raise AppException(
                    "CAN_TRANSFER",
                    f"This email is already registered. You can transfer to another committee ({transfers_left} transfer{'s' if transfers_left != 1 else ''} remaining).",
                    field="email",
                    status_code=409,
                    data=existing_data
                )
            else:
                raise AppException(
                    "TRANSFER_LIMIT_REACHED",
                    "This email is already registered. You have reached the maximum transfers limit.",
                    field="email",
                    status_code=409,
                    data=existing_data
                )

        # Step 2 — Duplicate student ID check
        existing = db.query(Delegate).filter(Delegate.student_id_cnic == data.student_id_cnic).first()
        if existing:
            # Check if this delegate can still transfer
            can_transfer = existing.transfer_count < MAX_TRANSFERS
            transfers_left = MAX_TRANSFERS - existing.transfer_count

            existing_data = {
                "roll_number": existing.roll_number,
                "full_name": existing.full_name,
                "committee": existing.committee.short_name if existing.committee else "N/A",
                "committee_full": existing.committee.full_name if existing.committee else "N/A",
                "transfer_count": existing.transfer_count,
                "can_transfer": can_transfer,
                "transfers_left": transfers_left,
                "is_final": not can_transfer,
                "final_committee": existing.committee.short_name,
                "final_roll_number": existing.roll_number
            }

            if can_transfer:
                raise AppException(
                    "CAN_TRANSFER",
                    f"This Student ID is already registered. You can transfer to another committee ({transfers_left} transfer{'s' if transfers_left != 1 else ''} remaining).",
                    field="student_id_cnic",
                    status_code=409,
                    data=existing_data
                )
            else:
                raise AppException(
                    "TRANSFER_LIMIT_REACHED",
                    "This Student ID is already registered. You have reached the maximum transfers limit.",
                    field="student_id_cnic",
                    status_code=409,
                    data=existing_data
                )

        # Step 3 — Lock committee row (SELECT FOR UPDATE)
        committee = (
            db.query(Committee)
            .filter(Committee.id == data.committee_id)
            .with_for_update()
            .first()
        )

        # Step 4 — Committee existence + active check
        if not committee or not committee.is_active:
            raise AppException("COMMITTEE_NOT_FOUND", "Selected committee not found.", field="committee_id")

        # Step 5 — Capacity check
        if committee.filled_seats >= committee.total_seats:
            message = f"{committee.short_name} is full. Please contact the LGUMUN society for assistance."
            contact = committee.contact_info
            data = {"contact_info": contact} if contact else {}
            raise AppException("COMMITTEE_FULL", message, field="committee_id", data=data)

        # Step 6 — Generate committee-scoped roll number using last_sequence
        committee.last_sequence += 1
        sequence = committee.last_sequence
        roll_number = f"LGU-{committee.short_name}-{sequence:0{ROLL_NUMBER_DIGITS}d}"

        # Step 7 — Insert delegate
        delegate = Delegate(
            roll_number=roll_number,
            full_name=data.full_name,
            student_id_cnic=data.student_id_cnic,
            email=data.email,
            phone=data.phone,
            institution=data.institution,
            committee_id=data.committee_id,
            ip_address=ip,
        )
        db.add(delegate)

        # Step 8 — Increment filled_seats atomically
        committee.filled_seats += 1
        db.commit()

        return {
            "roll_number": roll_number,
            "full_name": delegate.full_name,
            "email": delegate.email,
            "committee_name": committee.full_name,
            "committee_short_name": committee.short_name,
        }

    except AppException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"register_delegate failed: {e}", exc_info=True)
        if "UNIQUE" in str(e).upper() or "duplicate" in str(e).lower():
            if "email" in str(e).lower():
                raise AppException("DUPLICATE_EMAIL", "This email is already registered.", field="email")
            if "student_id_cnic" in str(e).lower() or "student_id" in str(e).lower():
                raise AppException("DUPLICATE_ID", "This Student ID / CNIC is already registered.", field="student_id_cnic")
        raise AppException("SERVER_ERROR", "Registration failed. Please try again.", status_code=500)

def get_delegates_count(db: Session) -> dict:
    count = db.query(func.count(Delegate.id)).scalar()
    return {"count": count}

def transfer_delegate(db: Session, roll_number: str, new_committee_id: int) -> dict:
    """Transfer a delegate from their current committee to a new one.

    Locks both committees with SELECT FOR UPDATE to prevent race conditions.
    Validates the destination committee exists, is active, and has capacity.
    """
    try:
        # Step 1 — Find delegate
        delegate = db.query(Delegate).filter(Delegate.roll_number == roll_number).first()
        if not delegate:
            raise AppException("DELEGATE_NOT_FOUND", "Delegate with that roll number not found.", status_code=404)

        # Prevent transferring to the same committee
        if delegate.committee_id == new_committee_id:
            raise AppException(
                "SAME_COMMITTEE",
                "Delegate is already in that committee.",
                field="new_committee_id",
            )

        # Step 2 — Lock both committee rows in consistent ID order to avoid deadlocks
        lower_id = min(delegate.committee_id, new_committee_id)
        higher_id = max(delegate.committee_id, new_committee_id)

        committees = (
            db.query(Committee)
            .filter(Committee.id.in_([lower_id, higher_id]))
            .with_for_update()
            .all()
        )
        committee_map = {c.id: c for c in committees}

        old_committee = committee_map.get(delegate.committee_id)
        new_committee = committee_map.get(new_committee_id)

        # Step 3 — Validate destination committee
        if not new_committee or not new_committee.is_active:
            raise AppException("COMMITTEE_NOT_FOUND", "Destination committee not found.", field="new_committee_id")

        # Step 4 — Capacity check on destination
        if new_committee.filled_seats >= new_committee.total_seats:
            message = f"{new_committee.short_name} is full. Please contact the LGUMUN society for assistance."
            contact = new_committee.contact_info
            data = {"contact_info": contact} if contact else {}
            raise AppException("COMMITTEE_FULL", message, field="new_committee_id", data=data)

        # Step 5 — Check transfer limit
        if delegate.transfer_count >= MAX_TRANSFERS:
            raise AppException(
                "TRANSFER_LIMIT_REACHED",
                f"You have already used your maximum of {MAX_TRANSFERS} transfers. Your current committee ({delegate.committee.short_name}) and roll number ({delegate.roll_number}) is FINAL.",
                field="new_committee_id",
                status_code=409,
                data={
                    "committee": delegate.committee.short_name,
                    "committee_full": delegate.committee.full_name,
                    "roll_number": delegate.roll_number,
                    "is_final": True,
                }
            )

        # Step 6 — Generate new roll number for the new committee
        new_committee.last_sequence += 1
        new_sequence = new_committee.last_sequence
        new_roll_number = f"LGU-{new_committee.short_name}-{new_sequence:0{ROLL_NUMBER_DIGITS}d}"

        # Step 7 — Perform the transfer
        old_committee_name = old_committee.full_name if old_committee else "Unknown"
        old_committee_short = old_committee.short_name if old_committee else "???"

        delegate.previous_committee_id = delegate.committee_id
        delegate.committee_id = new_committee_id
        delegate.roll_number = new_roll_number  # Update to new roll number
        delegate.transfer_count += 1
        delegate.transferred_at = datetime.now(timezone.utc)

        # Adjust seat counts
        if old_committee and old_committee.filled_seats > 0:
            old_committee.filled_seats -= 1
        new_committee.filled_seats += 1

        db.commit()

        # Check if this was the FINAL transfer (2nd)
        is_final = (delegate.transfer_count >= MAX_TRANSFERS)

        return {
            "roll_number": delegate.roll_number,
            "full_name": delegate.full_name,
            "email": delegate.email,
            "old_committee_name": old_committee_name,
            "old_committee_short_name": old_committee_short,
            "new_committee_name": new_committee.full_name,
            "new_committee_short_name": new_committee.short_name,
            "transferred_at": delegate.transferred_at.isoformat(),
            "transfer_count": delegate.transfer_count,
            "remaining_transfers": MAX_TRANSFERS - delegate.transfer_count,
            "is_final": is_final,
        }

    except AppException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"transfer_delegate failed: {e}", exc_info=True)
        raise AppException("SERVER_ERROR", "Transfer failed. Please try again.", status_code=500)


# ============================================================
# ADMIN SERVICES
# ============================================================

def get_admin_stats(db: Session) -> dict:
    """Get dashboard statistics for admin overview."""
    total_delegates = db.query(func.count(Delegate.id)).scalar() or 0

    all_committees = db.query(Committee).all()
    total_committees = len(all_committees)
    active_committees = len([c for c in all_committees if c.is_active])
    full_committees = len([c for c in all_committees if c.filled_seats >= c.total_seats])

    total_seats = sum(c.total_seats for c in all_committees)
    filled_seats = sum(c.filled_seats for c in all_committees)
    available_seats = total_seats - filled_seats
    fill_percentage = int((filled_seats / total_seats) * 100) if total_seats > 0 else 0

    return {
        "total_delegates": total_delegates,
        "total_committees": total_committees,
        "active_committees": active_committees,
        "full_committees": full_committees,
        "total_seats": total_seats,
        "filled_seats": filled_seats,
        "available_seats": available_seats,
        "fill_percentage": fill_percentage,
    }


def get_all_delegates_admin(db: Session, committee_id: int = None, search: str = None, page: int = 1, per_page: int = 20) -> dict:
    """Get paginated list of delegates with optional filters."""
    query = db.query(Delegate)

    if committee_id:
        query = query.filter(Delegate.committee_id == committee_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Delegate.full_name.ilike(search_pattern)) |
            (Delegate.roll_number.ilike(search_pattern)) |
            (Delegate.email.ilike(search_pattern)) |
            (Delegate.institution.ilike(search_pattern))
        )

    total = query.count()
    delegates = query.order_by(Delegate.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "delegates": [
            {
                "id": d.id,
                "roll_number": d.roll_number,
                "full_name": d.full_name,
                "email": d.email,
                "phone": d.phone,
                "institution": d.institution,
                "committee_id": d.committee_id,
                "committee": d.committee.short_name if d.committee else None,
                "committee_full": d.committee.full_name if d.committee else None,
                "transfer_count": d.transfer_count,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in delegates
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


def get_delegate_by_id_admin(db: Session, delegate_id: int) -> dict | None:
    """Get single delegate details."""
    delegate = db.query(Delegate).filter(Delegate.id == delegate_id).first()
    if not delegate:
        return None

    return {
        "id": delegate.id,
        "roll_number": delegate.roll_number,
        "full_name": delegate.full_name,
        "email": delegate.email,
        "phone": delegate.phone,
        "institution": delegate.institution,
        "committee_id": delegate.committee_id,
        "committee": delegate.committee.short_name if delegate.committee else None,
        "committee_full": delegate.committee.full_name if delegate.committee else None,
        "transfer_count": delegate.transfer_count,
        "previous_committee_id": delegate.previous_committee_id,
        "created_at": delegate.created_at.isoformat() if delegate.created_at else None,
        "transferred_at": delegate.transferred_at.isoformat() if delegate.transferred_at else None,
    }


def get_committees_for_admin(db: Session) -> list[dict]:
    """Get committees with extended admin info."""
    committees = db.query(Committee).all()
    return [
        {
            "id": c.id,
            "short_name": c.short_name,
            "full_name": c.full_name,
            "chair_name": c.chair_name,
            "agenda_1": c.agenda_1,
            "agenda_2": c.agenda_2,
            "total_seats": c.total_seats,
            "filled_seats": c.filled_seats,
            "available_seats": c.total_seats - c.filled_seats,
            "is_full": c.filled_seats >= c.total_seats,
            "capacity_percentage": int((c.filled_seats / c.total_seats) * 100) if c.total_seats > 0 else 0,
            "language": c.language,
            "is_active": c.is_active,
            "contact_info": c.contact_info,
        }
        for c in committees
    ]


def update_committee(db: Session, committee_id: int, chair_name: str = None, agenda_1: str = None, agenda_2: str = None, total_seats: int = None) -> dict | None:
    """Update committee details."""
    committee = db.query(Committee).filter(Committee.id == committee_id).first()
    if not committee:
        return None

    if chair_name is not None:
        committee.chair_name = chair_name
    if agenda_1 is not None:
        committee.agenda_1 = agenda_1
    if agenda_2 is not None:
        committee.agenda_2 = agenda_2
    if total_seats is not None:
        committee.total_seats = total_seats

    db.commit()
    db.refresh(committee)

    return {
        "id": committee.id,
        "short_name": committee.short_name,
        "full_name": committee.full_name,
        "chair_name": committee.chair_name,
        "agenda_1": committee.agenda_1,
        "total_seats": committee.total_seats,
        "filled_seats": committee.filled_seats,
    }


def create_query(db: Session, data: AdminQueryCreate, delegate_id: int) -> dict:
    """Create a new admin query."""
    query = AdminQuery(
        delegate_id=delegate_id,
        name=data.name,
        roll_number=data.roll_number,
        committee=data.committee,
        message=data.message,
        status="pending",
    )
    db.add(query)
    db.commit()
    db.refresh(query)

    return {
        "id": query.id,
        "name": query.name,
        "roll_number": query.roll_number,
        "committee": query.committee,
        "message": query.message,
        "status": query.status,
        "created_at": query.created_at.isoformat() if query.created_at else None,
    }


def get_queries(db: Session, status: str = None, page: int = 1, per_page: int = 20) -> dict:
    """Get paginated queries with optional status filter."""
    query = db.query(AdminQuery)

    if status and status != "all":
        query = query.filter(AdminQuery.status == status)

    total = query.count()
    queries = query.order_by(AdminQuery.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "queries": [
            {
                "id": q.id,
                "delegate_id": q.delegate_id,
                "name": q.name,
                "roll_number": q.roll_number,
                "committee": q.committee,
                "message": q.message,
                "status": q.status,
                "admin_reply": q.admin_reply,
                "replied_at": q.replied_at.isoformat() if q.replied_at else None,
                "created_at": q.created_at.isoformat() if q.created_at else None,
            }
            for q in queries
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


def reply_to_query(db: Session, query_id: int, reply: str) -> dict | None:
    """Reply to a query."""
    query = db.query(AdminQuery).filter(AdminQuery.id == query_id).first()
    if not query:
        return None

    query.admin_reply = reply
    query.replied_at = datetime.now(timezone.utc)
    query.status = "replied"

    db.commit()
    db.refresh(query)

    return {
        "id": query.id,
        "status": query.status,
        "admin_reply": query.admin_reply,
        "replied_at": query.replied_at.isoformat() if query.replied_at else None,
    }


def update_query_status(db: Session, query_id: int, status: str) -> dict | None:
    """Update query status."""
    query = db.query(AdminQuery).filter(AdminQuery.id == query_id).first()
    if not query:
        return None

    query.status = status
    db.commit()
    db.refresh(query)

    return {
        "id": query.id,
        "status": query.status,
    }


def get_settings(db: Session) -> list[dict]:
    """Get all system settings."""
    settings = db.query(SystemSettings).all()
    return [
        {
            "id": s.id,
            "key": s.key,
            "value": s.value,
            "description": s.description,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in settings
    ]


def update_setting(db: Session, key: str, value: str, description: str = None) -> dict:
    """Update a system setting."""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()

    if setting:
        setting.value = value
        if description is not None:
            setting.description = description
    else:
        setting = SystemSettings(key=key, value=value, description=description)
        db.add(setting)

    db.commit()
    db.refresh(setting)

    return {
        "id": setting.id,
        "key": setting.key,
        "value": setting.value,
        "description": setting.description,
    }


def export_delegates_csv(db: Session, committee_id: int = None) -> str:
    """Generate CSV export of delegates."""
    query = db.query(Delegate)

    if committee_id:
        query = query.filter(Delegate.committee_id == committee_id)

    delegates = query.order_by(Delegate.roll_number).all()

    # Build CSV content
    csv_lines = ["Roll Number,Full Name,Email,Phone,Institution,Committee,Transfer Count,Created At"]

    for d in delegates:
        csv_lines.append(
            f'{d.roll_number},"{d.full_name}",{d.email},{d.phone},"{d.institution}",{d.committee.short_name if d.committee else ""},{d.transfer_count},{d.created_at.isoformat() if d.created_at else ""}'
        )

    return "\n".join(csv_lines)

