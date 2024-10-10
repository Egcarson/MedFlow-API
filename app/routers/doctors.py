from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schema
from app.crud.doctors import doctor_crud_service
from app.database import get_db
from app.oauth2 import get_current_user


router = APIRouter(
    tags=['Doctors']
)


@router.get('/doctors', status_code=200, response_model=List[schema.Doctor])
async def get_doctors(db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    doctors = doctor_crud_service.get_all_doctors(db, offset, limit)

    return doctors

@router.get('/doctors/specialization', status_code=200, response_model=List[schema.Doctor])
async def get_doctor_by_specialization(specialization: str, db: Session = Depends(get_db), offset: int = 0, limit: int = 10):
    doctors = doctor_crud_service.get_doctor_by_specialization(db, specialization=specialization, offset=offset, limit=limit)

    if not doctors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Enter a valid specialization')
    
    if len(doctors) == 0:
        return {'message': 'No available doctors yet. Check at another time'}
    
    return doctors


@router.get('/doctors/{doctor_id}', status_code=200, response_model=schema.Doctor)
async def get_doctor_by_id(doctor_id: str, db: Session = Depends(get_db)):
    doctor = doctor_crud_service.get_doctor_by_id(db, doctor_id=doctor_id)

    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Doctor not found')
    
    return doctor

@router.post('/doctors/{doctor_id}/change_availability', status_code=200)
async def change_availability_status(doctor_id: int, db: Session = Depends(get_db), current_user: schema.Doctor = Depends(get_current_user)):
    doctor = doctor_crud_service.get_doctor_by_id(db, doctor_id=doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Doctor not found')
    
    if current_user.id != doctor_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized to make changes')
    
    doctor_crud_service.change_doctor_availability_status(db, doctor_id=doctor_id)

    return {"Status updated successfully!"}


@router.put('/doctors/{doctor_id}', status_code=200, response_model=schema.Doctor)
async def update_doctor(doctor_id: int, payload: schema.DoctorUpdate, db: Session = Depends(get_db), current_user: schema.Doctor = Depends(get_current_user)):
    doctor = doctor_crud_service.get_doctor_by_id(db, doctor_id=doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Doctor not found')
    
    if doctor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized to make changes')
    
    updated_doctor = doctor_crud_service.update_doctor(db, payload=payload, doctor_id=doctor_id)

    return updated_doctor


@router.delete('/doctors/{doctor_id}', status_code=200)
async def delete_doctor(doctor_id: int, db: Session = Depends(get_db), current_user: schema.Doctor = Depends(get_current_user)):
    doctor = doctor_crud_service.get_doctor_by_id(db, doctor_id=doctor_id)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Doctor not found')
    
    if doctor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authorized to make changes')

    doctor = doctor_crud_service.delete_doctor(db, doctor_id=doctor_id)

    return {'message': 'Deleted Successfully'}