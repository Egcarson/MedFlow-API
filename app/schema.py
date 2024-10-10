from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from enum import Enum
from typing import List

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PatientBase(BaseModel):
    title: str = "Mr"
    first_name: str = "John"
    last_name: str = "Doe"
    email: EmailStr
    phone_number: str
    date_of_birth: date
    gender: str
    age: Optional[int] = None
    address_line1: str
    address_line2: Optional[str] = None
    city: str = "Ikeja"
    state: str = "Lagos"
    zip_code: str
    country: str = "Nigeria"
    

class PatientCreate(PatientBase):
    password: str
    hospital_card_id: str = "MEDFLOW/PAT/24/001"

class PatientUpdate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True

# Doctor schema definition
class DoctorBase(BaseModel):
    title: str = "Dr."
    first_name: str = "Henry"
    last_name: str = "Ojeh"
    email: EmailStr
    phone_number: str
    date_of_birth: date
    gender: str
    age: Optional[int] = None
    specialization: str = "Surgeon"
    address_line1: str
    address_line2: Optional[str] = None
    city: str = "Victoria Island"
    state: str = "Lagos"
    zip_code: str
    country: str = "Nigeria"
    hospital_id: str = "MEDFLOW/MED/SG/001"
    

class DoctorCreate(DoctorBase):
    password: str

class DoctorUpdate(DoctorBase):
    pass

class Doctor(DoctorBase):
    id: int
    is_available: bool = True


# Appointment schema definition
class AppointmentBase(BaseModel):
    diagnosis: str
    severity: str
    appointment_date: datetime
    status: AppointmentStatus = AppointmentStatus.PENDING

class AppointmentCreate(AppointmentBase):
    doctor_id: int


class AppointmentUpdate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    patient_id: int
    doctor_id: int
    emr_id: Optional[int] = None
    

    class Config:
        from_attributes = True

class AppointmentResponse(BaseModel):
    id: int
    diagnosis: str
    severity: str
    patient: Patient
    doctor: Doctor
    appointment_date: datetime
    status: AppointmentStatus = AppointmentStatus.PENDING

    class Config:
        from_attributes = True



# medical record schema definition
class EMRBase(BaseModel):
    patient_id: int
    
     

class EMRCreate(EMRBase):
    pass

class EMR(EMRBase):
    id: int
    appointments: List[Appointment]

    class Config:
        from_attributes = True

class EMRResponse(BaseModel):
    id: int
    patient_id: int
    appointments: List[Appointment]


class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str
    confirm_password: str

class AppointmentStatusSwitch(BaseModel):
    status: AppointmentStatus = AppointmentStatus.PENDING
