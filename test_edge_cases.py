import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000/api/v1"

def test_edge_cases():
    print("=== Edge Case Testing ===\n")
    
    # 1. Invalid committee ID
    print("1. Testing invalid committee ID...")
    r = requests.post(f"{BASE_URL}/delegates", json={
        "full_name": "Test User",
        "email": f"test_{int(time.time())}a@example.com",
        "phone": "+923001234567",
        "institution": "Test Uni",
        "student_id_cnic": f"ID_{int(time.time())}a",
        "committee_id": 99999  # Invalid
    })
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "COMMITTEE_NOT_FOUND"
    print("   ✅ Invalid committee rejected")
    
    # 2. Invalid transfer (same committee)
    print("2. Testing same committee transfer...")
    # Register first
    reg = requests.post(f"{BASE_URL}/delegates", json={
        "full_name": "Edge Tester",
        "email": f"test_{int(time.time())}b@example.com",
        "phone": "+923001234567",
        "institution": "Test Uni",
        "student_id_cnic": f"ID_{int(time.time())}b",
        "committee_id": 17
    })
    roll = reg.json()["data"]["roll_number"]
    # Try to transfer to same committee
    r = requests.post(f"{BASE_URL}/delegates/{roll}/transfer", json={"new_committee_id": 17})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "SAME_COMMITTEE"
    print("   ✅ Same committee transfer rejected")
    
    # 3. Invalid roll number for transfer
    print("3. Testing invalid roll number transfer...")
    r = requests.post(f"{BASE_URL}/delegates/INVALID-ROLL/transfer", json={"new_committee_id": 14})
    assert r.status_code == 404
    print("   ✅ Invalid roll number rejected")
    
    # 4. Missing required fields
    print("4. Testing missing required fields...")
    r = requests.post(f"{BASE_URL}/delegates", json={"full_name": "Incomplete"})
    assert r.status_code in [400, 422]
    print("   ✅ Missing fields rejected")
    
    # 5. Test full committee
    print("5. Testing full committee handling...")
    # First get current fills
    comms = requests.get(f"{BASE_URL}/committees").json()["data"]["committees"]
    full_comm = next((c for c in comms if c["is_full"]), None)
    if full_comm:
        print(f"   Found full committee: {full_comm['short_name']}")
    else:
        print("   ✅ No full committees yet")
    
    # 6. Concurrent registration (basic, no race conditions)
    print("6. Testing rapid sequential registrations...")
    emails = [f"rapid_{int(time.time())}_{i}@example.com" for i in range(5)]
    results = []
    for e in emails:
        r = requests.post(f"{BASE_URL}/delegates", json={
            "full_name": "Rapid Test",
            "email": e,
            "phone": "+923001234567",
            "institution": "Test",
            "student_id_cnic": f"RAPID_{e}",
            "committee_id": 17
        })
        results.append(r.status_code)
    
    success_count = sum(1 for s in results if s == 201)
    print(f"   Success: {success_count}/5")
    
    print("\n=== Edge Cases Completed ===")

if __name__ == "__main__":
    test_edge_cases()
