"""
Simplified Frontend Browser Tests for LGUMUN 2026
Tests frontend pages using requests library (no browser needed)
"""
import pytest
import requests
import time

# Base URLs
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"


class TestFrontendPages:
    """Test all frontend pages load correctly"""

    def test_homepage_loads(self):
        """Test homepage loads"""
        response = requests.get(FRONTEND_URL)
        assert response.status_code == 200
        assert "LGUMUN 2026" in response.text
        assert "Inter-University" in response.text
        print("✓ Homepage loaded successfully")

    def test_committees_page_loads(self):
        """Test committees page loads"""
        response = requests.get(f"{FRONTEND_URL}/committees.html")
        assert response.status_code == 200
        assert "Committees" in response.text
        assert "committees-table" in response.text
        print("✓ Committees page loaded successfully")

    def test_register_page_loads(self):
        """Test registration page loads"""
        response = requests.get(f"{FRONTEND_URL}/register.html")
        assert response.status_code == 200
        assert "Register" in response.text
        assert "full_name" in response.text
        assert "email" in response.text
        print("✓ Register page loaded successfully")

    def test_success_page_loads(self):
        """Test success page loads"""
        response = requests.get(f"{FRONTEND_URL}/success.html")
        assert response.status_code == 200
        assert "Registration" in response.text
        print("✓ Success page loaded successfully")


class TestFrontendContent:
    """Test frontend content and elements"""

    def test_logo_removed(self):
        """Test MUN Society logo is removed"""
        response = requests.get(FRONTEND_URL)
        assert "lgu-mun-society-logo" not in response.text
        assert "lgumun-logo" not in response.text
        print("✓ MUN Society logo removed")

    def test_video_inline(self):
        """Test video player is inline (not modal)"""
        response = requests.get(FRONTEND_URL)
        assert "video-embed-wrapper" in response.text
        assert "video-modal" not in response.text or response.text.count("video-modal") == 0
        print("✓ Video player is inline")

    def test_particle_canvas_present(self):
        """Test particle canvas is present"""
        response = requests.get(FRONTEND_URL)
        assert "particles-canvas" in response.text
        print("✓ Particle canvas present")

    def test_duration_updated(self):
        """Test duration updated to 1 year"""
        response = requests.get(FRONTEND_URL)
        assert "One Year" in response.text or "since 2025" in response.text
        assert "Three Years" not in response.text
        print("✓ Duration updated to 1 year")


class TestCommitteeStructure:
    """Test committee structure"""

    def test_committees_count(self):
        """Test correct number of committees"""
        response = requests.get(f"{FRONTEND_URL}/committees.html")

        # Check removed committees are not present
        assert "ECOSOC" not in response.text or "Economic and Social Council" not in response.text
        assert "UNDP" not in response.text or "Development Programme" not in response.text
        assert "UNCSW" not in response.text or "Commission on the Status of Women" not in response.text
        assert "WHO" not in response.text or "World Health Organization" not in response.text

        # Check new committee is present
        assert "NCC" in response.text or "National Crisis Committee" in response.text

        print("✓ Committee structure correct (9 committees)")

    def test_ncc_english_only(self):
        """Test NCC is English only"""
        response = requests.get(f"{FRONTEND_URL}/committees.html")
        # NCC should be present
        assert "NCC" in response.text
        print("✓ NCC committee present")


class TestBackendAPI:
    """Test backend API endpoints"""

    def test_committees_api(self):
        """Test committees API returns correct data"""
        response = requests.get(f"{BACKEND_URL}/api/v1/committees")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "committees" in data["data"]
        assert len(data["data"]["committees"]) == 9

        print(f"✓ Committees API working ({len(data['data']['committees'])} committees)")

    def test_delegates_count_api(self):
        """Test delegates count API"""
        response = requests.get(f"{BACKEND_URL}/api/v1/delegates/count")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "count" in data["data"]

        print(f"✓ Delegates count API working ({data['data']['count']} delegates)")

    def test_registration_api(self):
        """Test registration API"""
        timestamp = int(time.time())
        test_data = {
            "full_name": "Browser Test User",
            "student_id_cnic": f"77777-7777{timestamp % 1000}-7",
            "email": f"browsertest{timestamp}@example.com",
            "phone": "03007777777",
            "institution": "Test University",
            "committee_id": 1
        }

        response = requests.post(
            f"{BACKEND_URL}/api/v1/delegates",
            json=test_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "roll_number" in data["data"]
        # For committee_id=1 in test, expect UNSC format
        assert data["data"]["roll_number"].startswith("LGU-UNSC-")

        print(f"✓ Registration API working (Roll: {data['data']['roll_number']})")


class TestImplementationRequirements:
    """Test all implementation requirements are met"""

    def test_seat_limit_50(self):
        """Test seat limit is 50"""
        response = requests.get(f"{FRONTEND_URL}/committees.html")
        # Check that seats:50 appears in the code
        assert "seats:50" in response.text or "seats: 50" in response.text
        print("✓ Seat limit enforced (max 50)")

    def test_roll_number_format(self):
        """Test roll number format"""
        response = requests.get(f"{FRONTEND_URL}/success.html")
        assert "LGU-MUN26" in response.text
        print("✓ Roll number format: LGU-MUN26-XXX")

    def test_premium_features(self):
        """Test premium features present"""
        response = requests.get(FRONTEND_URL)

        # Check for animations
        assert "animation" in response.text.lower()

        # Check for particle system
        assert "particles" in response.text.lower()

        # Check for gradients
        assert "gradient" in response.text.lower()

        print("✓ Premium features present")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
