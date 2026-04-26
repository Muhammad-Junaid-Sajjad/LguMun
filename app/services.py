import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Committee, Delegate, AdminQuery, SystemSettings
from app.schemas import DelegateCreate, CommitteeResponse, AdminQueryCreate, AdminQueryResponse, QueryReply, QueryStatusUpdate, SystemSettingCreate, SystemSettingResponse, AdminStats
from app.exceptions import AppException
from app.constants import ROLL_NUMBER_PREFIX, ROLL_NUMBER_DIGITS, MAX_TRANSFERS, ADMIN_API_KEY_HEADER
from app.email_service import send_registration_confirmation

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
    logger.info("Registration attempt for email: %s, institution: %s, IP: %s",
                data.email, data.institution, ip)
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
    except AppException as e:
        db.rollback()
        logger.warning("Registration AppException: %s - %s", e.code, e.message)
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Registration unexpected error")
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

    except AppException as e:
        db.rollback()
        logger.warning("Transfer AppException: %s - %s", e.code, e.message)
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Transfer unexpected error")
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


# ═══════════════════════════════════════════════════════════════════════════════
# GAP-001: DELEGATE QUERY SYSTEM (Public-facing)
# ═══════════════════════════════════════════════════════════════════════════════

def create_delegate_query(db: Session, data: dict) -> dict:
    """Create a new delegate query with human-readable tracking ID."""
    from app.models import DelegateQuery

    # Generate tracking ID: QRY-2026-0047
    year = datetime.now().year
    last_query = db.query(DelegateQuery).filter(
        DelegateQuery.tracking_id.like(f"QRY-{year}-%")
    ).order_by(DelegateQuery.id.desc()).first()

    if last_query:
        try:
            last_num = int(last_query.tracking_id.split("-")[-1])
            next_num = last_num + 1
        except:
            next_num = 1
    else:
        next_num = 1

    tracking_id = f"QRY-{year}-{next_num:04d}"

    # Check if delegate exists in database
    delegate = db.query(Delegate).filter(Delegate.roll_number == data["roll_number"]).first()
    delegate_id = delegate.id if delegate else None

    query = DelegateQuery(
        tracking_id=tracking_id,
        delegate_id=delegate_id,
        roll_number=data["roll_number"],
        name=data["name"],
        email=data["email"],
        category=data["category"],
        message=data["message"],
        status="submitted",
    )
    db.add(query)
    db.commit()
    db.refresh(query)

    return {
        "id": query.id,
        "tracking_id": query.tracking_id,
        "roll_number": query.roll_number,
        "name": query.name,
        "status": query.status,
        "created_at": query.created_at.isoformat() if query.created_at else None,
    }


def get_delegate_query_by_tracking(db: Session, tracking_id: str) -> dict | None:
    """Get query status by tracking ID (for delegate checking)."""
    from app.models import DelegateQuery

    query = db.query(DelegateQuery).filter(DelegateQuery.tracking_id == tracking_id).first()
    if not query:
        return None

    return {
        "id": query.id,
        "tracking_id": query.tracking_id,
        "category": query.category,
        "message": query.message,
        "status": query.status,
        "admin_reply": query.admin_reply,
        "replied_at": query.replied_at.isoformat() if query.replied_at else None,
        "created_at": query.created_at.isoformat() if query.created_at else None,
    }


def get_all_delegate_queries_admin(db: Session, status: str = "all", page: int = 1, per_page: int = 20) -> dict:
    """Get all delegate queries for admin panel."""
    from app.models import DelegateQuery

    query = db.query(DelegateQuery)

    if status and status != "all":
        query = query.filter(DelegateQuery.status == status)

    total = query.count()
    queries = query.order_by(DelegateQuery.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "queries": [
            {
                "id": q.id,
                "tracking_id": q.tracking_id,
                "delegate_id": q.delegate_id,
                "roll_number": q.roll_number,
                "name": q.name,
                "email": q.email,
                "category": q.category,
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
        "total_pages": (total + per_page - 1) // per_page if total > 0 else 1,
    }


def reply_delegate_query(db: Session, query_id: int, reply: str) -> dict | None:
    """Reply to a delegate query."""
    from app.models import DelegateQuery

    query = db.query(DelegateQuery).filter(DelegateQuery.id == query_id).first()
    if not query:
        return None

    query.admin_reply = reply
    query.replied_at = datetime.now(timezone.utc)
    query.status = "replied"

    db.commit()
    db.refresh(query)

    return {
        "id": query.id,
        "tracking_id": query.tracking_id,
        "status": query.status,
        "admin_reply": query.admin_reply,
        "replied_at": query.replied_at.isoformat() if query.replied_at else None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GAP-003: ANNOUNCEMENTS SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

def create_announcement(db: Session, data: dict, created_by: str) -> dict:
    """Create a new announcement."""
    from app.models import Announcement

    announcement = Announcement(
        title=data["title"],
        message=data["message"],
        priority=data.get("priority", "normal"),
        target=data.get("target", "all"),
        target_committee_id=data.get("target_committee_id"),
        day=data.get("day"),
        created_by=created_by,
        is_active=True,
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)

    return {
        "id": announcement.id,
        "title": announcement.title,
        "message": announcement.message,
        "priority": announcement.priority,
        "target": announcement.target,
        "created_at": announcement.created_at.isoformat() if announcement.created_at else None,
    }


def get_active_announcements(db: Session) -> list[dict]:
    """Get all active announcements (for polling)."""
    from app.models import Announcement

    announcements = db.query(Announcement).filter(
        Announcement.is_active == True
    ).order_by(Announcement.created_at.desc()).all()

    return [
        {
            "id": a.id,
            "title": a.title,
            "message": a.message,
            "priority": a.priority,
            "target": a.target,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in announcements
    ]


def get_all_announcements_admin(db: Session) -> list[dict]:
    """Get all announcements (active and archived) for admin."""
    from app.models import Announcement

    announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).all()

    return [
        {
            "id": a.id,
            "title": a.title,
            "message": a.message,
            "priority": a.priority,
            "target": a.target,
            "day": a.day,
            "is_active": a.is_active,
            "dismissed_at": a.dismissed_at.isoformat() if a.dismissed_at else None,
            "created_by": a.created_by,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in announcements
    ]


def dismiss_announcement(db: Session, announcement_id: int) -> dict | None:
    """Dismiss an announcement."""
    from app.models import Announcement

    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        return None

    announcement.is_active = False
    announcement.dismissed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(announcement)

    return {
        "id": announcement.id,
        "is_active": announcement.is_active,
        "dismissed_at": announcement.dismissed_at.isoformat() if announcement.dismissed_at else None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GAP-004: COUNTRY ALLOCATION ENGINE - COMPREHENSIVE
# ═══════════════════════════════════════════════════════════════════════════════

# P5 / Veto Powers (Tier 1 - Always first)
P5_COUNTRIES = {"USA", "United States", "US", "China", "Russia", "Russian Federation", "UK", "United Kingdom", "France"}

# Regional Powers & Major Players (2026 Context)
REGIONAL_POWERS = {
    "Middle East": {"Iran", "Israel", "Saudi Arabia", "UAE", "Qatar", "Turkey", "Egypt", "Jordan", "Lebanon", "Syria", "Iraq"},
    "South Asia": {"Pakistan", "India", "Afghanistan", "Bangladesh", "Sri Lanka", "Nepal", "Maldives"},
    "East Asia": {"Japan", "South Korea", "North Korea", "Taiwan", "Australia", "Indonesia", "Philippines", "Vietnam"},
    "Europe": {"Germany", "Italy", "Spain", "Poland", "Netherlands", "Belgium", "Ukraine"},
    "Africa": {"South Africa", "Nigeria", "Egypt", "Kenya", "Ethiopia", "Algeria", "Morocco"},
    "Americas": {"Brazil", "Mexico", "Canada", "Argentina", "Venezuela", "Cuba"}
}

# Countries with Active Conflicts / Hot/Cold War Relations
HOT_COLD_WAR_COUNTRIES = {
    "Israel-Hamas-Gaza": {"Israel", "Palestine", "Hamas", "Lebanon", "Iran", "Egypt", "Jordan", "Syria"},
    "Russia-Ukraine": {"Russia", "Ukraine", "Poland", "Germany", "USA", "UK", "France", "Belarus"},
    "Iran-Israel": {"Iran", "Israel", "USA", "Saudi Arabia", "UAE"},
    "India-Pakistan": {"India", "Pakistan", "China", "USA", "Afghanistan"},
    "US-China": {"USA", "China", "Taiwan", "Japan", "South Korea", "Australia", "Philippines"},
    "South China Sea": {"China", "Philippines", "Vietnam", "Japan", "USA", "Taiwan"}
}

# PNA Personalities (Alive 2026 - Pakistan Only)
PNA_PERSONALITIES = {
    "federal": [
        # Federal Leadership
        "Sheikh Hasina Wajid",  # PM (if applicable - Wazirobably different in 2026)
        "Asif Ali Zardari",  # President
        "Muhammad Shehbaz Sharif",  # PM
        "Maryam Nawaz",  # CM Punjab
        # Federal Ministers
        "Ishaq Dar",  # Finance Minister
        "Khawaja Muhammad Asif",  # Defence Minister
        "Bilawal Bhutto Zardari",  # Foreign Minister
        "Dr. Shamshad Akhtar",  # Interior Minister
        # Military Leadership (2026)
        "General Sahir Mesham",  # COAS ( Army Chief)
        "Lt General",  # DG ISI (placeholder)
        # Service Chiefs
        "Air Chief Marshal",  # Pakistan Air Force
        "Admiral",  # Pakistan Navy
    ],
    "mnas": [
        "Raja Riaz", "Murtaza Bhutto", "Shahid Khaqan Abbasi", "Hamza Shahbaz",
        "Shabana Kausar", "Fazal Khan", "Ali Amin Gandapur", "Omar Ayub",
        "Azam Khan Swati", "Mustafa Kamal", "Asad Qaiser", "Sheikh Rasheed"
    ],
    "mps": [
        "Sardar Bano", "Bilquees", "Mian Jamshed", "Imran Qureshi",
        "Sajid Mehdi", "Akbar", "Qamar-uz-Zaman"
    ],
    "provincial_leaders": [
        # Punjab
        "Maryam Nawaz", "Raja Bisma", "Marriyum Aurangzeb", "Azma Bukhari",
        # Sindh
        "Murad Ali Shah", "Saeed Ghani", "Syed Ali Zafar", "Karim Aayoob",
        # KPK
        "Ali Amin Khan Gandapur", "Mushtaq Ghani", "Kamran Bangash",
        # Balochistan
        "Sarbaz Khan", "Mir Zauru", "Jam Kamal",
        # Governors
        "Punjab Governor", "Sindh Governor", "KP Governor", "Balochistan Governor",
        "GB Governor", "AJK President"
    ],
    "political_leaders": [
        # PMLN
        "Nawaz Sharif", "Shehbaz Sharif", "Maryam Nawaz", "Ishaq Dar", "Ahsan Iqbal",
        "Rana Sanaullah", "Khawaja Asif", "Shahid Khaqan Abbasi",
        # PPP
        "Asif Ali Zardari", "Bilawal Bhutto Zardari", "Faryal Talpur", "Benazir Bhutto",
        "Raja Pervez Ashraf", "Saleem Mandviwalla",
        # PTI
        "Imran Khan", "Fawad Chaudhary", "Shah Mahmood Qureshi", "Asad Umar",
        "Hina Rabbani", "Zulfi Bukhari", "Shahid Kapoor",
        # Jamaat-e-Islami
        "Siraj-ul-Haq", "Mithapal",
        # Others
        "Gohar Ibrahim", "Mansoor Ali", "Sahibzada Hamid"
    ],
    "regional_leaders": [
        # Sindh
        "Bilawal Bhutto Zardari", "Qaim Ali Shah", "Syed Mustafa Kamal",
        "Saeed Ghani", "Karim Aayoob",
        # Balochistan
        "Jam Kamal Khan", "Sarbaz Khan", "Mir Abdul Qadir",
        # KP/FATA
        "Mafti Shahab", "Arif Yousufzai", "Ajab Khan",
        # GB/AJK
        "Mehmood Khan", "Sardar Bahadur", "Khan Hussain"
    ],
    "judiciary": [
        "Chief Justice Qazi Faez Isa", "Justice Yahya Afridi", "Justice Athar Minallah",
        "Justice Malik Dilawar", "Justice Shahid Waheed", "Justice Aalia Neelum",
        "Attorney General", "President Supreme Court Bar"
    ],
    "defense": [
        "General Sahir Mesham", "DG ISI", "Major General", "Air Chief Marshal",
        "Admiral Pakistan Navy", "Defence Secretary", "Chairman Joint Chiefs"
    ]
}


def _classify_country(value: str, agenda: str = "") -> tuple[int, str]:
    """Classify a country into tier and category based on agenda and global context.

    Returns: (tier 1-7, category string)
    """
    value_lower = value.lower().strip()
    agenda_lower = agenda.lower()

    # Tier 1: P5 / Veto Powers (MUST be first)
    if value_lower in {c.lower() for c in P5_COUNTRIES}:
        return (1, "P5")

    # Check agenda context for direct involvement
    if agenda_lower:
        # Extract key countries from agenda
        agenda_keywords = {
            "iran": {"iran", "tehran", "persian"},
            "israel": {"israel", "tel aviv", "jerusalem", "zionist"},
            "palestine": {"palestine", "gaza", "hamas", "west bank", "palestinian"},
            "ukraine": {"ukraine", "kiev", "russia", "crimea", "donbas"},
            "russia": {"russia", "moscow", "soviet", "putin"},
            "india": {"india", "delhi", "mumbai", "kashmir"},
            "pakistan": {"pakistan", "islamabad", "pakistani", "punjab", "sindh"},
            "china": {"china", "beijing", "taiwan", "hong kong", "xinjiang"},
            "korea": {"korea", "pyongyang", "seoul", "nuclear"},
            "afghanistan": {"afghanistan", "kabul", "taliban", "kabul"},
            "syria": {"syria", "damascus", "assad", "aleppo"},
            "iraq": {"iraq", "baghdad", "basra", "mosul"},
            "yemen": {"yemen", "sanaa", "houthis"},
            "turkey": {"turkey", "ankara", "istanbul", "erdogan"},
            "germany": {"germany", "berlin", "europe"},
            "france": {"france", "paris", "europe"},
            "uk": {"uk", "britain", "london", "england", "united kingdom"},
            "usa": {"usa", "america", "washington", "america"}
        }

        for key, keywords in agenda_keywords.items():
            if any(kw in agenda_lower for kw in keywords):
                if value_lower == key or any(kw in value_lower for kw in keywords):
                    return (2, "Directly Involved")

    # Tier 3: Regional Powers (check all regions)
    for region, countries in REGIONAL_POWERS.items():
        if value_lower in {c.lower() for c in countries}:
            return (3, f"Regional-{region}")

    # Tier 4: Hot/Cold War Countries
    for conflict, countries in HOT_COLD_WAR_COUNTRIES.items():
        if value_lower in {c.lower() for c in countries}:
            return (4, f"Conflict-{conflict}")

    # Tier 5: Neutral / Global Powers (Major economies, peaceful nations)
    NEUTRAL_POWERS = {
        "switzerland", "sweden", "norway", "finland", "denmark", "austria", "ireland",
        "portugal", "greece", "belgium", "netherlands", "luxembourg", "iceland",
        "canada", "australia", "new zealand", "singapore", "malaysia", "thailand",
        "vietnam", "argentina", "chile", "colombia", "peru", "uruguay", "south africa",
        "kenya", "morocco", "egypt", "tunisia", "algeria", "uae", "qatar", "kuwait",
        "oman", "bahrain", "jordan", "lebanon", "azerbaijan", "georgia", "armenia"
    }
    if value_lower in NEUTRAL_POWERS:
        return (5, "Neutral/Global")

    # Tier 6: Victim / Oppressor nations (based on agenda context)
    # These are typically identified from specific conflicts in agenda
    if agenda_lower:
        if any(term in agenda_lower for term in ["victim", "oppressed", "war crime", "genocide"]):
            # Victim countries in common conflicts
            if "gaza" in agenda_lower or "palestine" in agenda_lower:
                if value_lower in {"palestine", "gaza", "palestinian"}:
                    return (6, "Victim")
            if "ukraine" in agenda_lower:
                if value_lower == "ukraine":
                    return (6, "Victim")

    # Tier 7: Other / Remaining countries
    return (7, "Other")


def _classify_personality(value: str) -> tuple[int, str]:
    """Classify a personality for PNA committee.

    Returns: (tier, category)
    """
    value_lower = value.lower()

    # Tier 1: Supreme Leadership
    if any(x in value_lower for x in ["army chief", "coas", "general", "chief of army"]):
        return (1, "Military")
    if any(x in value_lower for x in ["president", "prime minister", "pm", "chairman"]):
        return (1, "Federal-Top")
    if any(x in value_lower for x in ["chief justice", "judge", "supreme"]):
        return (1, "Judiciary")

    # Tier 2: Federal Ministers & Service Chiefs
    if any(x in value_lower for x in ["minister", "secretary", "advisor"]):
        return (2, "Federal")
    if any(x in value_lower for x in ["air chief", "admiral", "director", "chief"]):
        return (2, "Service-Chiefs")

    # Tier 3: MNAs/MPAs
    if any(x in value_lower for x in ["mna", "mpa", "member of parliament", "senator"]):
        return (3, "Legislative")

    # Tier 4: Provincial Leadership
    if any(x in value_lower for x in ["chief minister", "cm", "governor", "provincial"]):
        return (4, "Provincial")
    if any(x in value_lower for x in ["balochistan", "sindh", "punjab", "kpk", "khan", "pakistan"]):
        if any(x in value_lower for x in ["leader", "politician", "chief"]):
            return (4, "Regional-Political")

    # Tier 5: Other Political Leaders
    if any(x in value_lower for x in ["zardari", "bhutto", "nawaz", "sharif", "khan", "imran", "jaat"]):
        return (5, "Political-Party")
    if any(x in value_lower for x in ["pmln", "ppp", "pti", "ji", " Jamaat"]):
        return (5, "Political-Party")

    # Tier 6: Legal/Advocacy
    if any(x in value_lower for x in ["barrister", "lawyer", "advocate", "attorney", "ag"]):
        return (6, "Legal")

    # Tier 7: General / Other
    return (7, "Other")


def set_committee_country_list(db: Session, committee_id: int, values: list[str], alloc_type: str = "country", agenda: str = "") -> dict:
    """Step 1: Load country/personality list for a committee with auto-classification."""
    from app.models import CommitteeAllocationPool, Committee

    if not agenda:
        committee = db.query(Committee).filter(Committee.id == committee_id).first()
        if committee:
            agenda = f"{committee.agenda_1 or ''} {committee.agenda_2 or ''}"

    db.query(CommitteeAllocationPool).filter(CommitteeAllocationPool.committee_id == committee_id).delete()

    parsed_values = []
    if isinstance(values, str):
        items = re.split(r'[,;\n]+', values)
        parsed_values = [v.strip() for v in items if v.strip()]
    elif isinstance(values, list):
        parsed_values = values
    else:
        parsed_values = [str(values)]

    tier_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    categories = set()

    for val in parsed_values:
        if not val.strip(): continue
        if alloc_type == "personality":
            tier, category = _classify_personality(val)
        else:
            tier, category = _classify_country(val, agenda)

        item = CommitteeAllocationPool(
            committee_id=committee_id,
            allocation_type=alloc_type,
            value=val.strip(),
            tier=tier,
            category=category,
            source="admin_input"
        )
        db.add(item)
        tier_counts[tier] += 1
        categories.add(category)

    db.commit()
    return {
        "count": len(parsed_values),
        "type": alloc_type,
        "classification": {
            "tier_1_p5": tier_counts[1],
            "tier_2_direct": tier_counts[2],
            "tier_3_regional": tier_counts[3],
            "tier_4_conflict": tier_counts[4],
            "tier_5_neutral": tier_counts[5],
            "tier_6_victim": tier_counts[6],
            "tier_7_other": tier_counts[7],
        },
        "categories": list(categories)
    }


def auto_assign_countries(db: Session, committee_id: int, strategy: str = "smart") -> dict:
    """Step 2: Assign countries to delegates based on strategy and constraints.

    Rules:
    - Tier 1 (P5) mandatory and assigned first.
    - Tier 2-6 assigned in order.
    - Tier 7 (Global Pool) fills remaining slots.
    - Check blocked_assignments for conflicts.
    - Handle dual-delegate support.
    """
    import random
    from app.models import (
        Delegate, CommitteeAllocationPool, CountryAllocation,
        BlockedAssignment, GlobalCountryPool
    )

    # 1. Get all delegates in this committee (order by registration)
    delegates = db.query(Delegate).filter(
        Delegate.committee_id == committee_id
    ).order_by(Delegate.created_at).all()

    if not delegates:
        raise AppException("NO_DELEGATES", "No delegates found in this committee to assign.")

    # 2. Get available items from Committee Allocation Pool (Active only)
    # This includes admin-inputted countries and pre-seeded personalities
    pool_items = db.query(CommitteeAllocationPool).filter(
        CommitteeAllocationPool.committee_id == committee_id,
        CommitteeAllocationPool.is_active == True
    ).order_by(CommitteeAllocationPool.tier).all()

    # 3. If pool is insufficient, fill from Global Country Pool (Tier 7)
    if len(pool_items) < len(delegates):
        needed = len(delegates) - len(pool_items)
        # Get random countries from global pool that aren't already in the committee pool
        existing_values = {p.value.lower() for p in pool_items}
        global_fallback = db.query(GlobalCountryPool).filter(
            GlobalCountryPool.is_active == True
        ).all()

        # Filter out existing and shuffle
        available_fallback = [g for g in global_fallback if g.name.lower() not in existing_values]
        random.shuffle(available_fallback)

        for i in range(min(needed, len(available_fallback))):
            fallback_item = CommitteeAllocationPool(
                committee_id=committee_id,
                value=available_fallback[i].name,
                allocation_type="country",
                tier=7,
                category="Global Fallback",
                source="global_pool"
            )
            pool_items.append(fallback_item)

    if len(pool_items) < len(delegates):
        raise AppException(
            "INSUFFICIENT_POOL",
            f"Need {len(delegates)} items but only {len(pool_items)} available including fallback."
        )

    # 4. Clear ALL existing allocations for this committee to prevent unique violation
    db.query(CountryAllocation).filter(
        CountryAllocation.committee_id == committee_id
    ).delete()

    # 5. Get Blocked Assignments for this committee
    blocked = db.query(BlockedAssignment).filter(
        BlockedAssignment.committee_id == committee_id
    ).all()
    blocked_map = {} # delegate_id -> set of blocked values
    for b in blocked:
        if b.delegate_id not in blocked_map:
            blocked_map[b.delegate_id] = set()
        blocked_map[b.delegate_id].add(b.blocked_value.lower())

    # 6. Allocation Algorithm
    # We use a greedy approach respecting tiers
    # For dual-delegate support, we keep track of how many times a value is used
    assignments = []
    used_indices = set()

    # Sort pool items: Tier 1 first, then 2, etc.
    pool_items.sort(key=lambda x: x.tier)

    for delegate in delegates:
        assigned = False
        delegate_blocks = blocked_map.get(delegate.id, set())

        # Try to find best fit from pool
        for idx, item in enumerate(pool_items):
            if idx in used_indices: continue

            # Check block list
            if item.value.lower() in delegate_blocks:
                continue

            # Found a match
            alloc = CountryAllocation(
                delegate_id=delegate.id,
                committee_id=committee_id,
                allocation_type=item.allocation_type,
                tier=item.tier,
                category=item.category,
                assigned_value=item.value,
                is_dual_pair=False, # We'll handle dual later if requested
                is_locked=False,
                is_published=False
            )
            db.add(alloc)
            assignments.append(alloc)
            used_indices.add(idx)
            assigned = True
            break

        if not assigned:
            # This should rarely happen if pool is large enough
            # but we fallback to first available unassigned if blocked everywhere
            for idx, item in enumerate(pool_items):
                if idx not in used_indices:
                    alloc = CountryAllocation(
                        delegate_id=delegate.id,
                        committee_id=committee_id,
                        allocation_type=item.allocation_type,
                        tier=item.tier,
                        category=item.category,
                        assigned_value=item.value,
                        is_published=False
                    )
                    db.add(alloc)
                    assignments.append(alloc)
                    used_indices.add(idx)
                    break

    db.commit()
    return {
        "assigned_count": len(assignments),
        "tier_summary": {
            "p5": sum(1 for a in assignments if a.tier == 1),
            "priority": sum(1 for a in assignments if 1 < a.tier <= 3),
            "fallback": sum(1 for a in assignments if a.tier == 7)
        }
    }


def add_blocked_assignment(db: Session, committee_id: int, delegate_id: int, value: str, reason: str = None) -> dict:
    """Add a conflict-of-interest block for a delegate."""
    from app.models import BlockedAssignment

    # Check if exists
    existing = db.query(BlockedAssignment).filter(
        BlockedAssignment.committee_id == committee_id,
        BlockedAssignment.delegate_id == delegate_id,
        BlockedAssignment.blocked_value == value
    ).first()

    if existing:
        return {"status": "already_exists", "id": existing.id}

    block = BlockedAssignment(
        committee_id=committee_id,
        delegate_id=delegate_id,
        blocked_value=value,
        reason=reason
    )
    db.add(block)
    db.commit()
    return {"status": "created", "id": block.id}


def toggle_pool_item_status(db: Session, item_id: int, is_active: bool) -> dict:
    """Activate/Deactivate a personality or country in the pool."""
    from app.models import CommitteeAllocationPool

    item = db.query(CommitteeAllocationPool).filter(CommitteeAllocationPool.id == item_id).first()
    if not item:
        raise AppException("ITEM_NOT_FOUND", "Pool item not found")

    item.is_active = is_active
    db.commit()
    return {"id": item.id, "is_active": item.is_active}


def get_global_countries(db: Session, region: str = None) -> list[dict]:
    """Get list of countries from global pool for admin selection."""
    from app.models import GlobalCountryPool

    query = db.query(GlobalCountryPool).filter(GlobalCountryPool.is_active == True)
    if region:
        query = query.filter(GlobalCountryPool.region == region)

    countries = query.order_by(GlobalCountryPool.name).all()
    return [{"name": c.name, "region": c.region, "subregion": c.subregion} for c in countries]


def import_to_committee_pool(db: Session, committee_id: int, values: list[str], tier: int = 5) -> dict:
    """Import values from global pool to committee-specific pool."""
    from app.models import CommitteeAllocationPool

    count = 0
    for val in values:
        # Check if already in pool
        existing = db.query(CommitteeAllocationPool).filter(
            CommitteeAllocationPool.committee_id == committee_id,
            CommitteeAllocationPool.value == val
        ).first()

        if not existing:
            # Auto-classify based on name
            tier_val, category = _classify_country(val)
            item = CommitteeAllocationPool(
                committee_id=committee_id,
                value=val,
                allocation_type="country",
                tier=tier_val or tier,
                category=category,
                source="global_pool"
            )
            db.add(item)
            count += 1

    db.commit()
    return {"imported_count": count}


def get_committee_allocations(db: Session, committee_id: int, include_unpublished: bool = True) -> list[dict]:
    """Step 3: Review current draft allocations.

    Args:
        db: Database session
        committee_id: ID of the committee
        include_unpublished: If True, include unpublished allocations too

    Returns:
        List of allocation records with tier and category info
    """
    from app.models import CountryAllocation, Delegate

    query = db.query(CountryAllocation).join(Delegate).filter(
        CountryAllocation.committee_id == committee_id
    )

    if not include_unpublished:
        query = query.filter(CountryAllocation.is_published == True)

    allocs = query.order_by(CountryAllocation.tier, "assigned_value").all()

    # Group by tier for better visualization
    result = []
    for a in allocs:
        tier_labels = {
            1: "P5/Veto",
            2: "Directly Involved",
            3: "Regional Power",
            4: "Conflict Party",
            5: "Neutral/Global",
            6: "Victim/Oppressor",
            7: "Other"
        }
        result.append({
            "id": a.id,
            "delegate_name": a.delegate.full_name,
            "roll_number": a.delegate.roll_number,
            "assigned_value": a.assigned_value,
            "tier": a.tier,
            "tier_label": tier_labels.get(a.tier, "Unknown"),
            "category": a.category,
            "is_locked": a.is_locked,
            "is_published": a.is_published
        })

    return result


def update_allocation(db: Session, allocation_id: int, new_value: str = None, is_locked: bool = None) -> dict:
    """Admin can update a single allocation (swap, lock/unlock)."""
    from app.models import CountryAllocation

    alloc = db.query(CountryAllocation).filter(CountryAllocation.id == allocation_id).first()
    if not alloc:
        raise AppException("ALLOCATION_NOT_FOUND", "Allocation not found")

    if new_value:
        alloc.assigned_value = new_value
    if is_locked is not None:
        alloc.is_locked = is_locked

    db.commit()

    return {
        "id": alloc.id,
        "assigned_value": alloc.assigned_value,
        "is_locked": alloc.is_locked
    }


def publish_committee_allocations(db: Session, committee_id: int) -> dict:
    """Step 4: Finalize and publish allocations, trigger emails."""
    from app.models import CountryAllocation, Delegate

    allocs = db.query(CountryAllocation).filter(
        CountryAllocation.committee_id == committee_id,
        CountryAllocation.is_published == False
    ).all()

    count = 0
    published_values = []

    for a in allocs:
        a.is_published = True
        a.published_at = datetime.now(timezone.utc)
        count += 1
        published_values.append({
            "delegate": a.delegate.full_name,
            "roll_number": a.delegate.roll_number,
            "assigned": a.assigned_value,
            "tier": a.tier
        })

        # Trigger email notification (if configured)
        # send_country_assignment(a.delegate.email, a.delegate.full_name, a.assigned_value)

    db.commit()

    return {
        "published_count": count,
        "allocations": published_values
    }


def get_allocation_preview(db: Session, committee_id: int) -> dict:
    """Get a preview of the allocation breakdown by tier before assignment."""
    from app.models import CountryList, Delegate

    # Count delegates
    delegate_count = db.query(Delegate).filter(Delegate.committee_id == committee_id).count()

    # Count available countries by tier
    items = db.query(CountryList).filter(CountryList.committee_id == committee_id).all()

    tier_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    tier_labels = {
        1: "P5/Veto Powers",
        2: "Directly Involved",
        3: "Regional Powers",
        4: "Hot/Cold War Parties",
        5: "Neutral/Global Powers",
        6: "Victim/Oppressor Nations",
        7: "Other"
    }

    for item in items:
        tier_counts[item.tier] += 1

    return {
        "committee_id": committee_id,
        "delegate_count": delegate_count,
        "country_count": len(items),
        "sufficient": len(items) >= delegate_count,
        "shortage": max(0, delegate_count - len(items)),
        "tier_breakdown": [
            {
                "tier": tier,
                "label": tier_labels[tier],
                "count": tier_counts[tier],
                "countries": [item.value for item in items if item.tier == tier]
            }
            for tier in range(1, 8) if tier_counts[tier] > 0
        ]
    }

