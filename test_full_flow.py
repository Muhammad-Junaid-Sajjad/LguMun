import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_registration_and_transfer():
    print("--- Starting Full System Test ---")
    
    # 1. Register a new delegate
    email = f"test_{int(time.time())}@example.com"
    reg_data = {
        "full_name": "Automated Tester",
        "email": email,
        "phone": "+923001234567",
        "institution": "LGU",
        "student_id_cnic": f"ID_{int(time.time())}",
        "committee_id": 17  # JSP
    }
    
    print(f"Testing Registration for {email}...")
    response = requests.post(f"{BASE_URL}/delegates", json=reg_data)
    print(f"Status: {response.status_code}")
    assert response.status_code == 201
    
    reg_result = response.json()["data"]
    roll_number = reg_result["roll_number"]
    print(f"Registered successfully! Roll Number: {roll_number}")
    
    # 2. Duplicate registration attempt (should trigger CAN_TRANSFER)
    print("Testing Duplicate Registration (expecting CAN_TRANSFER)...")
    response = requests.post(f"{BASE_URL}/delegates", json=reg_data)
    print(f"Status: {response.status_code}")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CAN_TRANSFER"
    print("Duplicate check passed.")
    
    # 3. Perform 1st Transfer
    print("Testing 1st Transfer (JSP -> UNODC [14])...")
    transfer_data = {"new_committee_id": 14}
    response = requests.post(f"{BASE_URL}/delegates/{roll_number}/transfer", json=transfer_data)
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    
    transfer_result = response.json()["data"]
    new_roll_number = transfer_result["roll_number"]
    print(f"1st Transfer success! New Roll Number: {new_roll_number}, Count: {transfer_result['transfer_count']}")
    assert transfer_result["transfer_count"] == 1
    
    # 4. Perform 2nd Transfer (Final)
    print("Testing 2nd Transfer (Final)...")
    transfer_data = {"new_committee_id": 17}  # Transfer back to JSP
    response = requests.post(f"{BASE_URL}/delegates/{new_roll_number}/transfer", json=transfer_data)
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    
    transfer_result = response.json()["data"]
    final_roll_number = transfer_result["roll_number"]
    print(f"2nd Transfer success! New Roll Number: {final_roll_number}, Count: {transfer_result['transfer_count']}")
    assert transfer_result["transfer_count"] == 2
    assert transfer_result["is_final"] == True
    
    # 5. Attempt 3rd Transfer (Should be blocked)
    print("Testing 3rd Transfer (expecting block)...")
    transfer_data = {"new_committee_id": 14}
    response = requests.post(f"{BASE_URL}/delegates/{final_roll_number}/transfer", json=transfer_data)
    print(f"Status: {response.status_code}")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "TRANSFER_LIMIT_REACHED"
    print("3rd Transfer correctly blocked.")
    
    print("--- Full System Test Completed Successfully! ---")

if __name__ == "__main__":
    test_registration_and_transfer()
