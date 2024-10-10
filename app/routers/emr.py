from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app import models, schema, oauth2
from app.crud.patients import patient_crud_service
from app.crud.appointment import get_uncompleted_appointments
from app.crud.doctors import doctor_crud_service as doc_crud
from app.database import get_db
from app.oauth2 import get_current_user
from app.crud.emr import emr_crud_service # type: ignore


router = APIRouter(
    tags=['Emr']
)


# @router.get('/emr/uncompleted_appointments/{patient_id}', status_code=200)
# async def uncompleted_appointments(patient_id: int, db: Session = Depends(get_db), doctor_current_user: models.Doctor = Depends(oauth2.get_current_user)):
    
#     patient = patient_crud_service.get_patient_by_id(id=patient_id, db=db)
#     if not patient:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Emr with patient id not found')
    
#     # uncompleted_apt = db.query(models.EMR).filter(models.EMR.appointments)

#     # if patient_current_user.id != patient_id:
#     #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Patient not authorized to view records')
    

#     # This logic is just to make sure that only doctors with uncompleted appointments with patient can check the record
#     appointments = get_uncompleted_appointments(patient_id=patient_id, db=db)

#     if not appointments:
#         return {"No unfinshed appointments found for this patient."}

#     doctors_id = [appointment.doctor_id for appointment in appointments]

#     if doctor_current_user.id not in doctors_id:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not authorized to view these records')
    
#     # Emr = emr_crud_service.get_patient_EMR(db=db, patient_id=patient_id)

#     # if not Emr:
#     #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No record for this patient')
    
#     return appointments

@router.get('/emr/patient_records/{patient_id}', status_code=200, response_model=List[schema.EMRResponse])
async def get_patient_records(patient_id: int, db: Session = Depends(get_db), doctor_current_user: models.Doctor = Depends(oauth2.get_current_user)):
    
    patient = patient_crud_service.get_patient_by_id(id=patient_id, db=db)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Emr with patient id not found')
    
    doc_validate = emr_crud_service.validate_patient_doctor(patient_id, doctor_current_user.id, db)

    doctors_id = [doctors.doctor_id for doctors in doc_validate]

    if doctor_current_user.id not in doctors_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not authorized to view these records')
    
    patient_emrs = emr_crud_service.get_patient_EMR(patient_id, db)

    return patient_emrs

@router.post('/emr/{patient_id}', status_code=201, response_model=schema.EMRResponse)
async def create_record(patient_id: int,  payload: schema.EMRCreate, db: Session = Depends(get_db), current_user: models.Doctor = Depends(get_current_user)):
    patient = patient_crud_service.get_patient_by_id(patient_id, db)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Patient not found')
    
    doctor_validate = doc_crud.get_doctor_by_id(db=db, doctor_id=current_user.id)
    if doctor_validate.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized')
    
    Emr = emr_crud_service.create_patient_EMR(db, payload, patient_id)

    return Emr


@router.delete('/emr/{emr_id}', status_code=status.HTTP_202_ACCEPTED)
async def delete_record(patient_id: int, emr_id: int, db: Session = Depends(get_db), current_user: models.Doctor = Depends(get_current_user)):
    emr = emr_crud_service.get_patient_EMR2(patient_id, emr_id, db)
    
    if not emr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Record not found')

    doc_validate = emr_crud_service.validate_patient_doctor(patient_id, current_user.id, db)

    doctors_id = [doctors.doctor_id for doctors in doc_validate]

    if current_user.id not in doctors_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You can not perform the requested action')

    emr_crud_service.delete_patient_EMR(emr.id, emr.patient_id, db)

    return {'message': 'Record deleted successfully'}
