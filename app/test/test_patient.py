from datetime import datetime
import pytest


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


@pytest.fixture
def patient_update_payload():
    return {
        "title": "Mr",
        "first_name":  "Joseph",
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

def test_get_patients(client, setup_database, patient_payload, patient_payload2):
    
    # Signup patients
    response = client.post(
        "/signup/patient", json=patient_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["email"] == "patient@email.com"
    assert data["state"] == "Lagos"

    assert "password" not in data

    response = client.post(
        "/signup/patient", json=patient_payload2)

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["email"] == "patient2@email.com"
    assert data["state"] == "Lagos"

    assert "password" not in data

    # Test get_patients endpoint

    response = client.get("/patients")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert all("first_name" in patient for patient in data)
    assert all("email" in patient for patient in data)
    assert all("last_name" in patient for patient in data)
    assert all("phone_number" in patient for patient in data)


@pytest.mark.parametrize("patient_id, wrong_id", [(1, 99)])
def test_get_patient_by_id(client, setup_database, patient_id, wrong_id):
    # Assert for invalid id
    response = client.get(f"/patients/{wrong_id}")
    assert response.status_code == 404

    response = client.get(f"/patients/{patient_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["first_name"] == "John"
    assert data["email"] == "patient@email.com"
    assert data["last_name"] == "Doe"


@pytest.mark.parametrize("email, password, patient_id, wrong_id, another_patient_id", [
    ("patient@email.com", "Password1234$", 1, 99, 2)
])
def test_update_patient(client, setup_database, email, password, patient_id, wrong_id, another_patient_id, patient_update_payload):

    # Login to authenticate
    response = client.post(
        "/login/", data={"username": email,  "password": password})

    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test authentication
    response = client.put(f"/patients/{patient_id}", json=patient_update_payload)
    assert response.status_code == 401

    # Test to update patient not in db
    response = client.put(f"/patients/{wrong_id}", json=patient_update_payload,
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": f"The patient with id '{wrong_id}' does not exist"}

    # Test update patient endpoint
    response = client.put(f"/patients/{patient_id}", json=patient_update_payload,
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 202
    data = response.json()
    assert data["first_name"] == patient_update_payload["first_name"]
    assert data["last_name"] == patient_update_payload["last_name"]

    # Test to see if an authenticated user can edit another_user (should throw a 401 because not authorized to do so)
    response = client.put(f"/patients/{another_patient_id}", json=patient_update_payload,
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "You are not authorized to perform this action."}


@pytest.mark.parametrize("email, password, patient_id, wrong_id, another_patient_id", [("patient@email.com", "Password1234$", 1, 99, 2)])
def test_delete_patient(client, setup_database, email, password, patient_id, wrong_id, another_patient_id):

    # Login to authenticate
    response = client.post(
        "/login/", data={"username": email,  "password": password})

    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test for authentication
    response = client.delete(f"/patients/{patient_id}")
    assert response.status_code == 401

    # Test to delete patient not in db
    response = client.delete(f"/patients/{wrong_id}",
                             headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": f"The patient with id '{wrong_id}' does not exist"}

    # Test if authenticated user can delete another user
    response = client.delete(f"/patients/{another_patient_id}",
                             headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "You are not authorized to perform this action."}

    # Test Authenticated user can delete account
    response = client.delete(
        f"/patients/{patient_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 202
    data = response.json()
    assert data == {"message": "Account deleted successfully!"}
