from datetime import datetime
import pytest

from app.schema import AppointmentStatus




@pytest.fixture
def emr_payload():
    return {
        "patient_id": 1
    }


@pytest.fixture
def appointment_payload():
    return {
        "doctor_id": 1,
        "diagnosis": "Malaria",
        "severity": "Mild",
        "appointment_date": datetime(1987, 4, 25).date().isoformat()
    }


@pytest.fixture
def doctor_payload():
    return {
        "title": "Dr.",
        "first_name": "Henry",
        "last_name": "Ojeh",
        "email": "doctor@email.com",
        "phone_number": "0801234567",
        "date_of_birth": datetime(1987, 4, 25).date().isoformat(),
        "gender": "Male",
        "age": 33,
        "specialization": "Surgeon",
        "address_line1": "15, doctor house",
        "address_line2": "20, doctor avenue",
        "city": "Victoria Island",
        "state": "Lagos",
        "zip_code": "23401",
        "country": "Nigeria",
        "hospital_id": "MEDFLOW/MED/SG/001",
        "password": "Password1234$"
    }


@pytest.fixture
def patient_payload():
    return {
        "title": "Mr",
        "first_name":  "John",
        "last_name": "Doe",
        "email": "patient@email.com",
        "phone_number": "0901111111",
        "date_of_birth": datetime(1990, 4, 25).date().isoformat(),
        "gender": "Male",
        "age": 49,
        "address_line1": "60, ikeja street 1",
        "address_line2": "60, ikeja street",
        "city": "Ikeja",
        "state":  "Lagos",
        "zip_code": "23401",
        "country": "Nigeria",
        "hospital_card_id": "MEDFLOW/PAT/24/001",
        "password": "Password1234$"
    }


@pytest.mark.parametrize("patient_id, wrong_id", [(1, 99)])
def test_create_emr(client, setup_database, emr_payload, patient_id, wrong_id, patient_payload, doctor_payload):
    
    # Signup doctor
    response = client.post(
        "/signup/doctor", json=doctor_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Henry"
    assert data["email"] == "doctor@email.com"
    assert data["state"] == "Lagos"

    assert "password" not in data

    # Signup patient
    response = client.post(
        "/signup/patient", json=patient_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["email"] == "patient@email.com"
    assert data["state"] == "Lagos"

    assert "password" not in data

    # Login to authenticate
    response = client.post(
        "/login", data={"username": "doctor@email.com",  "password": "Password1234$"})
    
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test create emr without authentication
    response = client.post(
        f"/emr/{patient_id}", json=emr_payload)

    assert response.status_code == 401

    # Test create emr with wrong id
    response = client.post(
        f"/emr/{wrong_id}", json=emr_payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Patient not found"}

    # Test with authentication
    response = client.post(
        f"/emr/{patient_id}", json=emr_payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201
    

@pytest.mark.parametrize("patient_id, wrong_id", [(1, 99)])
def test_get_emr(client, setup_database, patient_id, wrong_id, appointment_payload):

    # Login patient
    response = client.post(
        "/login", data={"username": "patient@email.com",  "password": "Password1234$"})
    
    assert response.status_code == 200
    patient_token = response.json()["access_token"]

    
    # Create appointment
    response = client.post(
                f"/appointments/{patient_id}", json=appointment_payload,
                headers={"Authorization": f"Bearer {patient_token}"})
    
    
    assert response.status_code == 201

    response = client.get(
        f"/emr/patient_records/{patient_id}")
    
    assert response.status_code == 401
    

    # Login doctor to authenticate
    response = client.post(
        "/login", data={"username": "doctor@email.com",  "password": "Password1234$"})

    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get(
        f"/emr/patient_records/{patient_id}", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200

    response = client.get(
        f"/emr/patient_records/{wrong_id}", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 404
    


@pytest.mark.parametrize("emr_id, wrong_id", [(1, 99)])
def test_delete_emr(client, setup_database, emr_id, wrong_id):
    # Login doctor to authenticate
    response = client.post(
        "/login", data={"username": "doctor@email.com",  "password": "Password1234$"})

    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.delete(
        f"/emr/{emr_id}/?patient_id=1")

    assert response.status_code == 401

    response = client.delete(
        f"/emr/{wrong_id}/?patient_id=1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404

    response = client.delete(
        f"/emr/{emr_id}/?patient_id=1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 202
