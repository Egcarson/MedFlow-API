from datetime import datetime
import pytest
from app.schema import AppointmentStatus


@pytest.fixture
def appointment_payload():
    return {
        "doctor_id": 1,
        "diagnosis": "Malaria",
        "severity": "Mild",
        "appointment_date": datetime(2024, 10, 25).date().isoformat(),
        "status": AppointmentStatus.PENDING
    }


@pytest.fixture
def appointment_update_payload():
    return {
        "diagnosis": "Fever",
        "severity": "Severe",
        "appointment_date": datetime(2024, 10, 25).date().isoformat(),
        "status": AppointmentStatus.PENDING
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


@pytest.fixture
def patient_payload2():
    return {
        "title": "Mrs",
        "first_name":  "Jane",
        "last_name": "Doe",
        "email": "patient2@email.com",
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
        "hospital_card_id": "MEDFLOW/PAT/24/002",
        "password": "Password1234$"
    }



@pytest.mark.parametrize("patient_id, wrong_id", [(1, 99)])
def test_create_appointment(client, setup_database, patient_id, wrong_id, patient_payload, doctor_payload, appointment_payload):
    
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
        "/login", data={"username": "patient@email.com",  "password": "Password1234$"})

    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test create appointment without authentication
    response = client.post(f"/appointments/{patient_id}", json=appointment_payload)

    assert response.status_code == 401
    
    # Test create appointment with non-existing user
    response = client.post(
        f"/appointments/{wrong_id}", json=appointment_payload,
        headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()
    assert data == {
        "detail": "The patient with id '%s' does not exist" % wrong_id}
    
    # Test create appointment endpoint
    response = client.post(
        f"/appointments/{patient_id}", json=appointment_payload,
        headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 201

@pytest.mark.parametrize("patient_id, wrong_id", [(1, 99)])
def test_get_appointment(client, setup_database, patient_id, wrong_id):

    # Login to authenticate
    response = client.post(
        "/login", data={"username": "patient@email.com",  "password": "Password1234$"})

    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test authentication
    response = client.get(
        f"/appointments/{patient_id}")
    
    assert response.status_code == 401
    
    # Test wrong patient id
    response = client.get(
        f"/appointments/{wrong_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()

    assert data == {
        "detail": "The patient with id '%s' does not exist" % wrong_id}

    # Test get appointment 
    response = client.get(
        f"/appointments/{patient_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200


def test_get_appointments(client, setup_database):

    response = client.get("/appointments")

    assert response.status_code == 200
    data = response.json()

    

    assert len(data) == 1
    assert all("diagnosis" in appointment for appointment in data)
    assert all("severity" in appointment for appointment in data)
    assert all("appointment_date" in appointment for appointment in data)


@pytest.mark.parametrize("email, password, appointment_id, wrong_id", [
    ("patient@email.com", "Password1234$", 1, 99)
])
def test_update_appointment(client, setup_database, email, password, appointment_id, wrong_id, appointment_update_payload, patient_payload2):

    # Login to authenticate
    response = client.post(
        "/login/", data={"username": email,  "password": password})

    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test authentication
    response = client.put(
        f"/appointments/{appointment_id}", json=appointment_update_payload)
    assert response.status_code == 401

    # Test to update appointment not in db
    response = client.put(f"/appointments/{wrong_id}", json=appointment_update_payload,
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    data = response.json()
    assert data == {
        "detail": "The appointment with id '%s' does not exist" % wrong_id}

    # Test update appointment endpoint
    response = client.put(f"/appointments/{appointment_id}", json=appointment_update_payload,
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 202
    data = response.json()
    assert data["diagnosis"] == appointment_update_payload["diagnosis"]
    assert data["severity"] == appointment_update_payload["severity"]

    # Test to see if an authenticated user can edit another users appointment (should throw a 401 because not authorized to do so)

    # Signup another user

    # Signup another patient
    response = client.post(
        "/signup/patient", json=patient_payload2)

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["email"] == "patient2@email.com"
    assert data["state"] == "Lagos"

    assert "password" not in data

    # Login new patient to authenticate
    response = client.post(
        "/login", data={"username": "patient2@email.com",  "password": "Password1234$"})
    
    assert response.status_code == 200
    new_patient_token = response.json()["access_token"]

    # Test to see if new patient can edit another patients appointment
    response = client.put(f"/appointments/{appointment_id}", json=appointment_update_payload,
                          headers={"Authorization": f"Bearer {new_patient_token}"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "You are not authorized to perform this action."}


@pytest.mark.parametrize("appointment_id, wrong_id", [(1, 99)])
def test_cancel_appointment(client, setup_database, appointment_id, wrong_id):
    # Login patient to authenticate
    response = client.post(
        "/login", data={"username": "patient@email.com",  "password": "Password1234$"})

    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.post(
        f"/appointments/{appointment_id}/cancel_appointment")

    assert response.status_code == 401
    

    response = client.post(
        f"/appointments/{wrong_id}/cancel_appointment", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()

    assert data == {
        "detail": "The appointment with id '%s' does not exist" % wrong_id}

    response = client.post(
        f"/appointments/{appointment_id}/cancel_appointment", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 202
