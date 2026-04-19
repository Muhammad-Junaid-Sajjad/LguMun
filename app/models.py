from sqlalchemy import (
    Column, Integer, String, Boolean, Text,
    ForeignKey, DateTime, func
)
from sqlalchemy.dialects.postgresql import INET
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
    language = Column(String(20), default="English")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    delegates = relationship("Delegate", back_populates="committee")

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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(INET, nullable=True)

    committee = relationship("Committee", back_populates="delegates")
