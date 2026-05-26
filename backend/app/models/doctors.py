from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Specialization(str, Enum):
    ORTHOPEDICS = "Orthopedics"
    GENERAL_SURGERY = "General Surgery"
    EMERGENCY_MEDICINE = "Emergency Medicine"
    NEUROLOGY = "Neurology"
    CARDIOLOGY = "Cardiology"
    TRAUMA_SURGEON = "Trauma Surgeon"
    GENERAL_PHYSICIAN = "General Physician"
    OTHER = "Other"


class DoctorBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")  # International format
    
    hospital_name: str
    clinic_address: str                    # Full address entered by doctor
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    specialization: Specialization
    experience_years: Optional[int] = Field(None, ge=0, le=60)
    
    accepts_emergency_reports: bool = True   # Consent for receiving patient reports
    is_available: bool = True                # Available for emergency cases
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DoctorCreate(DoctorBase):
    """Used when doctor registers"""
    pass


class DoctorResponse(DoctorBase):
    """Response model for API"""
    id: str
    
    class Config:
        from_attributes = True


class DoctorListResponse(BaseModel):
    """For returning list of doctors"""
    doctors: List[DoctorResponse]
    total: int