import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Committee, Delegate
from app.schemas import DelegateCreate, CommitteeResponse
from app.exceptions import AppException
from app.constants import ROLL_NUMBER_PREFIX, ROLL_NUMBER_DIGITS

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
        # Step 1 — Duplicate email check (case-insensitive already lowercased by schema)
        if db.query(Delegate).filter(Delegate.email == data.email).first():
            raise AppException("DUPLICATE_EMAIL", "This email is already registered.", field="email")

        # Step 2 — Duplicate student ID check
        if db.query(Delegate).filter(Delegate.student_id_cnic == data.student_id_cnic).first():
            raise AppException("DUPLICATE_ID", "This Student ID / CNIC is already registered.", field="student_id_cnic")

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
            raise AppException("COMMITTEE_FULL", f"{committee.short_name} is full. No seats available.", field="committee_id")

        # Step 6 — Generate sequential roll number
        sequence = db.query(func.count(Delegate.id)).scalar() + 1
        roll_number = f"{ROLL_NUMBER_PREFIX}-{sequence:0{ROLL_NUMBER_DIGITS}d}"

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
        raise AppException("SERVER_ERROR", "Registration failed. Please try again.", status_code=500)
