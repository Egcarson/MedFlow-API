from datetime import datetime
import pytest


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
def doctor_payload2():
    return {
        "title": "Dr.",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "doctor2@email.com",
        "phone_number": "0901234567",
        "date_of_birth": datetime(1987, 4, 25).date().isoformat(),
        "gender": "Male",
        "age": 33,
        "specialization": "Gynecologist",
        "address_line1": "15, doctor house",
        "address_line2": "20, doctor avenue",
        "city": "Victoria Island",
        "state": "Lagos",
        "zip_code": "23401",
        "country": "Nigeria",
        "hospital_id": "MEDFLOW/MED/SG/002",
        "password": "Password1234$"
    }


@pytest.fixture
def doctor_update_payload():
    return {
        "title": "Dr.",
        "first_name": "Jonathan",
        "last_name": "Goodluck",
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



def test_get_doctors(client, setup_database, doctor_payload, doctor_payload2):

    # Signup doctor
    response = client.post(
        "/signup/doctor", json=doctor_payload)

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Henry"
    assert data["email"] == "doctor@email.com"
    assert data["state"] == "Lagos"

    assert "password" not in data

    response = client.post(
        "/signup/doctor", json=doctor_payload2)

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["email"] == "doctor2@email.com"
    assert data["state"] == "Lagos"

    assert "password" not in data

    # Test get_doctor endpoint

    response = client.get("/doctors")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert all("first_name" in doctor for doctor in data)
    assert all("email" in doctor for doctor in data)
    assert all("last_name" in doctor for doctor in data)
    assert all("phone_number" in doctor for doctor in data)


@pytest.mark.parametrize("doctor_id, wrong_id", [(1, 99)])
def test_get_doctor_by_id(client, setup_database, doctor_id, wrong_id):
    # Assert for invalid id
    response = client.get(f"/doctors/{wrong_id}")
    assert response.status_code == 404

    # Assert valid doctor id
    response = client.get(f"/doctors/{doctor_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["first_name"] == "Henry"
    assert data["email"] == "doctor@email.com"
    assert data["last_name"] == "Ojeh"


def test_get_doctor_by_specialization(client, setup_database):
    # Assert for invalid specialization
    response = client.get("/doctors/specialization/?specialization=Nurse")
    assert response.status_code == 404

    response = client.get(f"/doctors/specialization/?specialization=Surgeon")

    assert response.status_code == 200
    data = response.json()

    assert all("first_name" in doctor for doctor in data)
    assert all("email" in doctor for doctor in data)
    assert all("last_name" in doctor for doctor in data)
    assert all("phone_number" in doctor for doctor in data)

    


@pytest.mark.parametrize("email, password, doctor_id, wrong_id, another_doctor_id", [
    ("doctor@email.com", "Password1234$", 1, 99, 2)
])
def test_update_doctor(client, setup_database, email, password, doctor_id, wrong_id, another_doctor_id, doctor_update_payload):

    # Login to authenticate
    response = client.post(
        "/login/", data={"username": email,  "password": password})

    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test authentication
    response = client.put(
        f"/doctors/{doctor_id}", json=doctor_update_payload)
    assert response.status_code == 401

    # Test to update doctor not in db
    response = client.put(f"/doctors/{wrong_id}", json=doctor_update_payload,
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Doctor not found"}

    response = client.put(f"/doctors/{doctor_id}", json=doctor_update_payload,
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == doctor_update_payload["first_name"]
    assert data["last_name"] == doctor_update_payload["last_name"]

    # Test to see if an authenticated doctor can edit another_doctor (should throw a 401 because not authorized to do so)
    response = client.put(f"/doctors/{another_doctor_id}", json=doctor_update_payload,
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Not authorized to make changes"}


@pytest.mark.parametrize("email, password, doctor_id, wrong_id, another_doctor_id", [
    ("doctor@email.com", "Password1234$", 1, 99, 2)
])
def test_change_doctor_availability_status(client, setup_database, email, password, doctor_id, wrong_id, another_doctor_id):
    # Login to authenticate
    response = client.post(
        "/login/", data={"username": email,  "password": password})

    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test authentication
    response = client.post(
        f"/doctors/{doctor_id}/change_availability")
    assert response.status_code == 401

    # Test to update doctor not in db
    response = client.post(f"/doctors/{wrong_id}/change_availability",
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Doctor not found"}

    # Test authenticated doctor
    response = client.post(f"/doctors/{doctor_id}/change_availability",
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data == ["Status updated successfully!"]
    

    # Test to see if an authenticated user can edit another_user (should throw a 401 because not authorized to do so)
    response = client.post(f"/doctors/{another_doctor_id}/change_availability",
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Not authorized to make changes"}


@pytest.mark.parametrize("email, password, doctor_id, wrong_id, another_doctor_id", [("doctor@email.com", "Password1234$", 1, 99, 2)])
def test_delete_doctor(client, setup_database, email, password, doctor_id, wrong_id, another_doctor_id):

    # Login to authenticate
    response = client.post(
        "/login/", data={"username": email,  "password": password})

    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test for authentication
    response = client.delete(f"/doctors/{doctor_id}")
    assert response.status_code == 401

    # Test to delete doctor not in db
    response = client.delete(f"/doctors/{wrong_id}",
                             headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Doctor not found"}

    # Test if authenticated doctor can delete another doctor
    response = client.delete(f"/doctors/{another_doctor_id}",
                             headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Not authorized to make changes"}

    # Test Authenticated doctor can delete account
    response = client.delete(
        f"/doctors/{doctor_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data == {"message": "Deleted Successfully"}
