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
    agenda_1 = Column(Text, default="To be announced")
    agenda_2 = Column(Text, nullable=True)
    total_seats = Column(Integer, nullable=False, default=30)
    filled_seats = Column(Integer, nullable=False, default=0)
    last_sequence = Column(Integer, nullable=False, default=0)
    language = Column(String(20), default="English")
    is_active = Column(Boolean, default=True)
    contact_info = Column(String(255), nullable=True)  # Contact info when full
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
    previous_committee_id = Column(Integer, ForeignKey("committees.id"), nullable=True)  # Track transfers
    transfer_count = Column(Integer, nullable=False, default=0)  # Number of times transferred (0-2)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    transferred_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6 as string

    committee = relationship("Committee", back_populates="delegates", foreign_keys=[committee_id])

class AdminQuery(Base):
    __tablename__ = "admin_queries"

    id = Column(Integer, primary_key=True, index=True)
    delegate_id = Column(Integer, ForeignKey("delegates.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    roll_number = Column(String(20), nullable=False, index=True)
    committee = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)

    # Status: pending, replied, resolved
    status = Column(String(20), nullable=False, default="pending")
    admin_reply = Column(Text, nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    delegate = relationship("Delegate")

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

