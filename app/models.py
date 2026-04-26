from sqlalchemy import (
    Column, Integer, String, Boolean, Text,
    ForeignKey, DateTime, func, Sequence, Enum
)
from sqlalchemy.orm import relationship
from app.database import Base

class Committee(Base):
    __tablename__ = "committees"

    id = Column(Integer, primary_key=True)
    short_name = Column(String(10), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    chair_name = Column(String(100), default="To be announced")
    acd_name = Column(String(100), nullable=True)  # NEW
    contact_email = Column(String(255), nullable=True)  # NEW
    agenda_1 = Column(Text, default="To be announced")
    agenda_2 = Column(Text, nullable=True)
    total_seats = Column(Integer, nullable=False, default=30)
    filled_seats = Column(Integer, nullable=False, default=0)
    last_sequence = Column(Integer, nullable=False, default=0)
    language = Column(String(20), default="English")
    is_active = Column(Boolean, default=True)
    contact_info = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    delegates = relationship("Delegate", back_populates="committee", foreign_keys="[Delegate.committee_id]")

class Delegate(Base):
    __tablename__ = "delegates"

    id = Column(Integer, primary_key=True)
    roll_number = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    student_id_cnic = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    institution = Column(String(200), nullable=False)
    committee_id = Column(Integer, ForeignKey("committees.id"), nullable=False, index=True)
    previous_committee_id = Column(Integer, ForeignKey("committees.id"), nullable=True)
    transfer_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    transferred_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String(45), nullable=True)
    # NOTE: country, day1_present, etc. are stored in separate tables

    committee = relationship("Committee", back_populates="delegates", foreign_keys=[committee_id])

class AdminQuery(Base):
    __tablename__ = "admin_queries"

    id = Column(Integer, primary_key=True, index=True)
    delegate_id = Column(Integer, ForeignKey("delegates.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    roll_number = Column(String(20), nullable=False, index=True)
    committee = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)

    status = Column(String(20), nullable=False, default="pending")
    admin_reply = Column(Text, nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    delegate = relationship("Delegate")

# NEW TABLES - Created separately via migration
class DelegateQuery(Base):
    """Public-facing delegate query system (GAP-001)"""
    __tablename__ = "delegate_queries"

    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(String(20), unique=True, nullable=False)
    delegate_id = Column(Integer, ForeignKey("delegates.id"), nullable=True)
    roll_number = Column(String(20), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)

    status = Column(String(20), default="submitted")
    admin_reply = Column(Text, nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    delegate = relationship("Delegate")

class Announcement(Base):
    """Real-time announcements system (GAP-003)"""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="normal")
    target = Column(String(20), nullable=False, default="all")
    target_committee_id = Column(Integer, ForeignKey("committees.id"), nullable=True)
    day = Column(Integer, nullable=True)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    dismissed_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    committee = relationship("Committee")

class CountryList(Base):
    """Country/Personality list per committee (GAP-004)"""
    __tablename__ = "country_lists"

    id = Column(Integer, primary_key=True, index=True)
    committee_id = Column(Integer, ForeignKey("committees.id"), nullable=False)
    allocation_type = Column(String(20), nullable=False)  # "country" or "personality"
    value = Column(String(200), nullable=False)
    tier = Column(Integer, default=5)  # 1=P5/Veto, 2=Directly Involved, 3=Regional Powers, 4=Hot/Cold War, 5=Neutral, 6=Agenda-Related, 7=Other
    category = Column(String(100), nullable=True)  # e.g., "P5", "Regional", "Neutral", "Victim", "Oppressor"
    is_assigned = Column(Boolean, default=False)

    committee = relationship("Committee")

class CountryAllocation(Base):
    """Actual allocation per delegate (GAP-004)"""
    __tablename__ = "country_allocations"

    id = Column(Integer, primary_key=True, index=True)
    delegate_id = Column(Integer, ForeignKey("delegates.id"), unique=True, nullable=False)
    committee_id = Column(Integer, ForeignKey("committees.id"), nullable=False)
    allocation_type = Column(String(20), nullable=False)  # "country" or "personality"
    tier = Column(Integer, default=5)  # Tier 1-7 classification
    category = Column(String(100), nullable=True)  # e.g., "P5", "Regional", "Neutral"
    assigned_value = Column(String(200), nullable=False)
    is_dual_pair = Column(Boolean, default=False)  # True if same value assigned to 2 delegates
    is_locked = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    delegate = relationship("Delegate", foreign_keys=[delegate_id])
    committee = relationship("Committee")

class Attendance(Base):
    """Daily attendance records (GAP-006)"""
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    delegate_id = Column(Integer, ForeignKey("delegates.id"), nullable=False)
    committee_id = Column(Integer, ForeignKey("committees.id"), nullable=False)
    day = Column(Integer, nullable=False)
    is_present = Column(Boolean, default=False)
    recorded_by = Column(String(100), nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=True)

    delegate = relationship("Delegate")
    committee = relationship("Committee")


class GlobalCountryPool(Base):
    """Global pool of all countries organized by region (197 countries)"""
    __tablename__ = "global_country_pool"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    region = Column(String(100), nullable=True)
    subregion = Column(String(100), nullable=True)
    iso_code = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CommitteeAllocationPool(Base):
    """Per-committee allocation pool + global personalities"""
    __tablename__ = "committee_allocation_pool"

    id = Column(Integer, primary_key=True, index=True)
    committee_id = Column(Integer, ForeignKey("committees.id"), nullable=True)  # NULL = global pool
    value = Column(String(200), nullable=False)
    allocation_type = Column(String(20), nullable=False)  # "country" or "personality"
    tier = Column(Integer, default=5)  # 1-7 priority classification
    category = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_dual_allowed = Column(Boolean, default=False)
    source = Column(String(50), default="admin_input")  # "admin_input" or "global_pool"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    committee = relationship("Committee")


class BlockedAssignment(Base):
    """Prevent delegate-country/personality conflicts"""
    __tablename__ = "blocked_assignments"

    id = Column(Integer, primary_key=True, index=True)
    committee_id = Column(Integer, ForeignKey("committees.id"), nullable=False)
    delegate_id = Column(Integer, ForeignKey("delegates.id"), nullable=False)
    blocked_value = Column(String(200), nullable=False)
    reason = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    committee = relationship("Committee")
    delegate = relationship("Delegate")

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())