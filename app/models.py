from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from app.schema import AppointmentStatus

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    title = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    age = Column(Integer)
    gender = Column(String, nullable=False)
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    hospital_card_id = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    appointments = relationship("Appointment", back_populates="patient")
    emr = relationship("EMR", back_populates="patient")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    title = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    age = Column(Integer)
    gender = Column(String, nullable=False)
    hospital_id = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True, index=True)
    specialization = Column(String, nullable=False)
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    password = Column(String, nullable=False)

    appointments = relationship("Appointment", back_populates="doctor")


class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    diagnosis = Column(Text, nullable=False)
    severity = Column(String(10), nullable=False)
    patient_id = Column(Integer, ForeignKey(
        "patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey(
        "doctors.id", ondelete="CASCADE"), nullable=False)
    emr_id = Column(Integer, ForeignKey(
        "emrs.id", ondelete="CASCADE"), nullable=True)
    appointment_date = Column(DateTime(timezone=True), nullable=False,
                              server_default=text('CURRENT_TIMESTAMP'))
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    emr = relationship("EMR", back_populates="appointments")


class EMR(Base):
    __tablename__ = 'emrs'

    id = Column(Integer, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    patient_id = Column(Integer, ForeignKey(
        "patients.id", ondelete="CASCADE"), nullable=False)

    appointments = relationship("Appointment", back_populates="emr")
    patient = relationship("Patient", back_populates="emr")
