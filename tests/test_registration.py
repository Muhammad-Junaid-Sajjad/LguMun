import pytest
from app.models import Delegate

def test_valid_registration(client, test_committee):
    """Test successful registration returns 201 with roll number"""
    response = client.post("/api/v1/delegates", json={
        "full_name": "John Doe",
        "student_id_cnic": "12345-1234567-1",
        "email": "john@example.com",
        "phone": "03001234567",
        "institution": "Test University",
        "committee_id": test_committee.id
    })
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "roll_number" in data["data"]
    assert data["data"]["roll_number"].startswith("LGU-MUN26-")

def test_duplicate_email(client, test_committee):
    """Test duplicate email returns 400 with DUPLICATE_EMAIL"""
    # First registration
    client.post("/api/v1/delegates", json={
        "full_name": "John Doe",
        "student_id_cnic": "12345-1234567-1",
        "email": "john@example.com",
        "phone": "03001234567",
        "institution": "Test University",
        "committee_id": test_committee.id
    })
    # Second registration with same email
    response = client.post("/api/v1/delegates", json={
        "full_name": "Jane Doe",
        "student_id_cnic": "12345-1234567-2",
        "email": "john@example.com",
        "phone": "03001234568",
        "institution": "Test University",
        "committee_id": test_committee.id
    })
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "DUPLICATE_EMAIL"

def test_duplicate_email_uppercase(client, test_committee):
    """Test duplicate email with uppercase returns 400 (case-insensitive)"""
    # First registration
    client.post("/api/v1/delegates", json={
        "full_name": "John Doe",
        "student_id_cnic": "12345-1234567-1",
        "email": "john@example.com",
        "phone": "03001234567",
        "institution": "Test University",
        "committee_id": test_committee.id
    })
    # Second registration with uppercase email
    response = client.post("/api/v1/delegates", json={
        "full_name": "Jane Doe",
        "student_id_cnic": "12345-1234567-2",
        "email": "JOHN@EXAMPLE.COM",
        "phone": "03001234568",
        "institution": "Test University",
        "committee_id": test_committee.id
    })
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "DUPLICATE_EMAIL"

def test_duplicate_student_id(client, test_committee):
    """Test duplicate student ID returns 400 with DUPLICATE_ID"""
    # First registration
    client.post("/api/v1/delegates", json={
        "full_name": "John Doe",
        "student_id_cnic": "12345-1234567-1",
        "email": "john@example.com",
        "phone": "03001234567",
        "institution": "Test University",
        "committee_id": test_committee.id
    })
    # Second registration with same student ID
    response = client.post("/api/v1/delegates", json={
        "full_name": "Jane Doe",
        "student_id_cnic": "12345-1234567-1",
        "email": "jane@example.com",
        "phone": "03001234568",
        "institution": "Test University",
        "committee_id": test_committee.id
    })
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "DUPLICATE_ID"

def test_full_committee(client, full_committee):
    """Test registration for full committee returns 400 with COMMITTEE_FULL"""
    response = client.post("/api/v1/delegates", json={
        "full_name": "John Doe",
        "student_id_cnic": "12345-1234567-1",
        "email": "john@example.com",
        "phone": "03001234567",
        "institution": "Test University",
        "committee_id": full_committee.id
    })
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "COMMITTEE_FULL"

def test_missing_field(client, test_committee):
    """Test missing required field returns 422"""
    response = client.post("/api/v1/delegates", json={
        "full_name": "John Doe",
        # Missing student_id_cnic
        "email": "john@example.com",
        "phone": "03001234567",
        "institution": "Test University",
        "committee_id": test_committee.id
    })
    assert response.status_code == 422

def test_invalid_phone(client, test_committee):
    """Test invalid phone format returns 422"""
    response = client.post("/api/v1/delegates", json={
        "full_name": "John Doe",
        "student_id_cnic": "12345-1234567-1",
        "email": "john@example.com",
        "phone": "12345",  # Invalid phone
        "institution": "Test University",
        "committee_id": test_committee.id
    })
    assert response.status_code == 422

def test_invalid_email(client, test_committee):
    """Test invalid email format returns 422"""
    response = client.post("/api/v1/delegates", json={
        "full_name": "John Doe",
        "student_id_cnic": "12345-1234567-1",
        "email": "invalid-email",  # Invalid email
        "phone": "03001234567",
        "institution": "Test University",
        "committee_id": test_committee.id
    })
    assert response.status_code == 422

def test_filled_seats_increments(client, test_committee, db_session):
    """Test filled_seats increments after registration"""
    initial_seats = test_committee.filled_seats
    assert initial_seats == 0

    client.post("/api/v1/delegates", json={
        "full_name": "John Doe",
        "student_id_cnic": "12345-1234567-1",
        "email": "john@example.com",
        "phone": "03001234567",
        "institution": "Test University",
        "committee_id": test_committee.id
    })

    # Refresh committee from DB
    db_session.refresh(test_committee)
    assert test_committee.filled_seats == 1

def test_get_committees(client, test_committee):
    """Test GET /committees returns all committees"""
    response = client.get("/api/v1/committees")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "committees" in data["data"]
    assert len(data["data"]["committees"]) > 0

def test_get_committee_not_found(client):
    """Test GET /committees/{id} returns 404 for non-existent committee"""
    response = client.get("/api/v1/committees/9999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
