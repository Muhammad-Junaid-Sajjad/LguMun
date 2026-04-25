# LGU MUN 2026 - Automated Test Runner

## Test Runner Script
# Run with: python3 tests/auto-runner.py

import subprocess
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_KEY = "lgumun2026_admin_secure_key_x9y2z"

def run_test(name, command, expected=None):
    """Run a single test and report result."""
    print(f"\n[TEST] {name}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"  ✓ PASSED")
            return True
        else:
            print(f"  ✗ FAILED: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

def test_api(endpoint, headers=None, method="GET", data=None):
    """Test an API endpoint."""
    import urllib.request
    import urllib.error

    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            req = urllib.request.Request(url)
        else:
            req = urllib.request.Request(url, data=json.dumps(data).encode(), method="POST")

        if headers:
            for k, v in headers.items():
                req.add_header(k, v)

        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": str(e), "code": e.code}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("="*50)
    print("LGUMUN 2026 - AUTOMATED TEST RUNNER")
    print(f"Started: {datetime.now()}")
    print("="*50)

    # Layer 2: API Tests
    print("\n" + "="*50)
    print("LAYER 2: API ENDPOINT TESTS")
    print("="*50)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Health
    result = test_api("/api/v1/health")
    if result.get("status") == "ok":
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 2: Committees
    result = test_api("/api/v1/committees")
    if result.get("success") and len(result["data"]["committees"]) == 9:
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 3: Delegate Count
    result = test_api("/api/v1/delegates/count")
    if result.get("success"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 4: Admin Stats
    result = test_api("/api/v1/admin/stats", {"X-Admin-API-Key": API_KEY})
    if result.get("success"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 5: Admin Committees
    result = test_api("/api/v1/admin/committees", {"X-Admin-API-Key": API_KEY})
    if result.get("success"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 6: Admin Settings
    result = test_api("/api/v1/admin/settings", {"X-Admin-API-Key": API_KEY})
    if result.get("success"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 7: Invalid API Key
    result = test_api("/api/v1/admin/stats", {"X-Admin-API-Key": "invalid"})
    if not result.get("success"):
        tests_passed += 1
    else:
        tests_failed += 1

    # Summary
    print("\n" + "="*50)
    print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")
    print("="*50)

    return 0 if tests_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())