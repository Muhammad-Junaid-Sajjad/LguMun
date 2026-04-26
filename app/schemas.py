import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from app.constants import PAKISTANI_PHONE_REGEX, MAX_NAME_LENGTH, MAX_INSTITUTION_LENGTH

class DelegateCreate(BaseModel):
    full_name: str
    student_id_cnic: str
    email: EmailStr
    phone: str
    institution: str
    committee_id: int

    @field_validator("full_name")
    @classmethod
    def name_length(cls, v):
        v = v.strip()
        if not v or len(v) > MAX_NAME_LENGTH:
            raise ValueError("Full name is required and must be under 200 characters")
        return v

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v):
        return v.lower().strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        digits_only = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(PAKISTANI_PHONE_REGEX, digits_only):
            raise ValueError("Enter a valid Pakistani phone number (e.g. 03001234567)")
        return digits_only

    @field_validator("student_id_cnic")
    @classmethod
    def clean_id(cls, v):
        return v.strip()

    @field_validator("institution")
    @classmethod
    def institution_length(cls, v):
        v = v.strip()
        if not v or len(v) > MAX_INSTITUTION_LENGTH:
            raise ValueError("Institution name is required and must be under 200 characters")
        return v

class DelegateResponse(BaseModel):
    roll_number: str
    full_name: str
    email: str
    committee_name: str
    committee_short_name: str

class CommitteeResponse(BaseModel):
    id: int
    short_name: str
    full_name: str
    chair_name: str
    acd_name: str
    contact_email: str | None
    agenda_1: str
    agenda_2: str | None
    total_seats: int
    filled_seats: int
    language: str
    contact_info: str | None
    is_full: bool
    capacity_percentage: int

    class Config:
        from_attributes = True

class TransferRequest(BaseModel):
    new_committee_id: int

class TransferResponse(BaseModel):
    roll_number: str
    full_name: str
    email: str
    old_committee_name: str
    old_committee_short_name: str
    new_committee_name: str
    new_committee_short_name: str
    transferred_at: str

class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    timestamp: str

# GAP-001: Delegate Query System
class DelegateQueryCreate(BaseModel):
    roll_number: str
    name: str
    email: EmailStr
    category: str
    message: str

class DelegateQueryResponse(BaseModel):
    id: int
    tracking_id: str
    roll_number: str
    name: str
    status: str
    admin_reply: str | None = None
    replied_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True

# GAP-003: Announcements
class AnnouncementCreate(BaseModel):
    title: str
    message: str
    priority: str = "normal"
    target: str = "all"
    target_committee_id: int | None = None
    day: int | None = None

class AnnouncementResponse(BaseModel):
    id: int
    title: str
    message: str
    priority: str
    target: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# Admin Portal Schemas
class AdminQueryBase(BaseModel):
    name: str
    roll_number: str
    committee: str
    message: str

class AdminQueryCreate(AdminQueryBase):
    pass

class AdminQueryResponse(AdminQueryBase):
    id: int
    delegate_id: int
    status: str
    admin_reply: str | None = None
    replied_at: str | None = None
    created_at: str

    class Config:
        from_attributes = True

class QueryReply(BaseModel):
    reply: str

class QueryStatusUpdate(BaseModel):
    status: str  # pending, replied, resolved

class SystemSettingBase(BaseModel):
    key: str
    value: str
    description: str | None = None

class SystemSettingCreate(SystemSettingBase):
    pass

class SystemSettingResponse(SystemSettingBase):
    id: int
    updated_at: str

    class Config:
        from_attributes = True

class AdminStats(BaseModel):
    total_delegates: int
    total_committees: int
    active_committees: int
    full_committees: int
    total_seats: int
    filled_seats: int
    available_seats: int
    fill_percentage: int
    pending_queries: int = 0
