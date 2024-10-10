from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from app.crud.patients import patient_crud_service as pat_crud
from app.crud import appointment as apt_crud
from app.crud.doctors import doctor_crud_service as doc_crud
from app import schema, database, models, oauth2

router = APIRouter(
    tags=['Appointments']
    )

@router.post('/appointments/{patient_id}', status_code=status.HTTP_201_CREATED, response_model=schema.AppointmentResponse)
def create_appointment(payload: schema.AppointmentCreate, patient_id: int, db: Session = Depends(database.get_db), current_user: models.Patient = Depends(oauth2.get_current_user)):
    patient = pat_crud.get_patient_by_id(patient_id, db)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The patient with id '%s' does not exist" % patient_id
        )
    
    #check if the patient has a pending appointment
    if apt_crud.check_pending_appointment(patient_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The patient already has a pending appointment. Please progress with the previous appointment or cancel it."
        )

    #check if the doctor
    #only patients can create an appointment
    if current_user.id != patient.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can create appointments."
        )
    
    #updating this session with doctor id validation
    doctor = doc_crud.get_doctor_by_id(db, payload.doctor_id)

    # validating availability of doctor in the database
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The doctor with id '%s' does not exist" % payload.doctor_id
        )

    # validate doctor status
    if doctor.is_available == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The doctor is not available at the moment."
        )

    appointment = apt_crud.create_appointment(payload, patient_id, db)

    doctor.is_available = False
    db.commit()
    db.refresh(doctor)

    return appointment

@router.get('/appointments/{patient_id}', status_code=status.HTTP_200_OK, response_model=List[schema.AppointmentResponse])
def get_appointments(patient_id: int, db: Session = Depends(database.get_db), current_user: models.Patient = Depends(oauth2.get_current_user)):
    patient = pat_crud.get_patient_by_id(patient_id, db)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The patient with id '%s' does not exist" % patient_id
        )
    
    appointments = apt_crud.get_appointments_by_patient_id(patient_id, db)

    return appointments

@router.get('/appointments', status_code=status.HTTP_200_OK, response_model=List[schema.AppointmentResponse])
def get_appointments(offset: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    appointments = apt_crud.get_appointment(offset, limit, db)
    return appointments

@router.put('/appointments/{appointment_id}', status_code=status.HTTP_202_ACCEPTED, response_model=schema.AppointmentResponse)
def update_appointment(appointment_id: int, payload: schema.AppointmentUpdate, db: Session = Depends(database.get_db), current_user: models.Patient = Depends(oauth2.get_current_user)):
    appointment = apt_crud.get_appointment_by_id(appointment_id, db)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The appointment with id '%s' does not exist" % appointment_id
        )
    
    if appointment.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this action."
        )
    
    appointment = apt_crud.update_appointment(appointment_id, payload, db)
    return appointment

@router.post('/appointments/{appointment_id}/cancel_appointment', status_code=status.HTTP_202_ACCEPTED)
def cancel_appointment(appointment_id: int, db: Session = Depends(database.get_db), current_user: models.Patient = Depends(oauth2.get_current_user)):
    appointment = apt_crud.get_appointment_by_id(appointment_id, db)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The appointment with id '%s' does not exist" % appointment_id
        )
    
    patient = pat_crud.get_patient_by_id(current_user.id, db)
    if appointment.patient_id != patient.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this action."
        )
    
    apt_crud.cancel_appointment(appointment_id, db)

    doctor = doc_crud.get_doctor_by_id(db, appointment.doctor_id)

    doctor.is_available = True
    db.commit()
    db.refresh(doctor)

    return {"message": "Appointment cancelled successfully"}