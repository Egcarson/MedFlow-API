import pytest
from datetime import datetime


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
def password_reset_payload():
    return {
        "email": "patient@email.com",
        "new_password": "NewPassword1234$",
        "confirm_password": "NewPassword1234$"
    }



def test_signup_patient(client, setup_database, patient_payload):
    response = client.post(
        "/signup/patient", json=patient_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["email"] == "patient@email.com"
    assert data["state"] == "Lagos"

    assert "password" not in data


def test_signup_existing_patient(client, setup_database, patient_payload):
    response = client.post(
        "/signup/patient", json=patient_payload)

    assert response.status_code == 409


def test_signup_doctor(client, setup_database, doctor_payload):
    response = client.post(
        "/signup/doctor", json=doctor_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Henry"
    assert data["email"] == "doctor@email.com"
    assert data["state"] == "Lagos"

    assert "password" not in data


def test_signup_existing_doctor(client, setup_database, doctor_payload):
    response = client.post(
        "/signup/doctor", json=doctor_payload)

    assert response.status_code == 409
  


@pytest.mark.parametrize("email, password, wrong_email, wrong_password", [("doctor@email.com", "Password1234$", "wrong@email.com", "wrong_password")])
def test_login(client, setup_database, email, password, wrong_email, wrong_password):

    # Login
    response = client.post(
        "/login", data={"username": email,  "password": password})

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Test Login with wrong email
    response = client.post(
        "/login/", data={"username": wrong_email,  "password": password})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Incorrect username or password"}

    # Test Login with incorrect password
    response = client.post(
        "/login/", data={"username": email,  "password": wrong_password})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Incorrect username or password"}


def test_password_reset(client, setup_database, password_reset_payload):
    response = client.post(
        "/auth/password_reset", json=password_reset_payload)
    
    assert response.status_code == 401
    
    # Login to authenticate
    response = client.post(
        "/login", data={"username": "doctor@email.com",  "password": "Password1234$"})

    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.post(
        "/auth/password_reset", json=password_reset_payload,
        headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 202
    data = response.json()
    assert data == {"details": "Password has been changed successfully!"}

