"""
Admin API endpoint tests.
Tests for admin authentication, stats, delegates, committees, queries, and settings.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from tests.conftest import test_db, override_get_db


@pytest.fixture
def admin_client():
    """Test client with admin API key header."""
    client = TestClient(app)
    client.headers["X-Admin-API-Key"] = "lgumun2026_admin_secure_key_x9y2z"
    return client


@pytest.fixture
def invalid_key_client():
    """Test client with invalid API key."""
    client = TestClient(app)
    client.headers["X-Admin-API-Key"] = "invalid_key_123"
    return client


class TestAdminAuthentication:
    """Test admin API key authentication."""

    def test_admin_rejects_invalid_key(self, invalid_key_client):
        """Invalid API key should be rejected."""
        response = invalid_key_client.get("/api/v1/admin/stats")
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "Invalid Admin API Key" in data["error"]["code"]

    def test_admin_accepts_valid_key(self, admin_client):
        """Valid API key should be accepted."""
        response = admin_client.get("/api/v1/admin/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestAdminStats:
    """Test admin dashboard stats endpoint."""

    def test_stats_returns_total_delegates(self, admin_client):
        """Stats should include total delegate count."""
        response = admin_client.get("/api/v1/admin/stats")
        data = response.json()
        assert "total_delegates" in data["data"]

    def test_stats_returns_committees(self, admin_client):
        """Stats should include committee counts."""
        response = admin_client.get("/api/v1/admin/stats")
        data = response.json()
        assert "total_committees" in data["data"]
        assert "active_committees" in data["data"]


class TestAdminDelegates:
    """Test admin delegate management endpoints."""

    def test_list_delegates_paginated(self, admin_client):
        """Delegates list should support pagination."""
        response = admin_client.get("/api/v1/admin/delegates?page=1&per_page=5")
        data = response.json()
        assert data["success"] is True
        assert "delegates" in data["data"]
        assert data["data"]["per_page"] == 5

    def test_get_single_delegate(self, admin_client):
        """Should get a single delegate by ID."""
        # First get a delegate ID from the list
        response = admin_client.get("/api/v1/admin/delegates?per_page=1")
        if response.json()["data"]["delegates"]:
            delegate_id = response.json()["data"]["delegates"][0]["id"]
            detail = admin_client.get(f"/api/v1/admin/delegates/{delegate_id}")
            assert detail.status_code == 200


class TestAdminCommittees:
    """Test admin committee management endpoints."""

    def test_list_committees(self, admin_client):
        """Should list all committees."""
        response = admin_client.get("/api/v1/admin/committees")
        data = response.json()
        assert data["success"] is True
        assert "committees" in data["data"]

    def test_update_committee(self, admin_client):
        """Should update a committee."""
        # First get committees
        resp = admin_client.get("/api/v1/admin/committees")
        committees = resp.json()["data"]["committees"]
        if committees:
            committee_id = committees[0]["id"]
            update_resp = admin_client.put(
                f"/api/v1/admin/committees/{committee_id}",
                json={"chair_name": "Test Chair"}
            )
            assert update_resp.status_code == 200


class TestAdminSettings:
    """Test admin settings management endpoints."""

    def test_get_settings(self, admin_client):
        """Should get all settings."""
        response = admin_client.get("/api/v1/admin/settings")
        data = response.json()
        assert data["success"] is True
        assert "settings" in data["data"]

    def test_update_setting(self, admin_client):
        """Should update a setting value."""
        # Find registration_open setting key
        response = admin_client.get("/api/v1/admin/settings")
        settings = response.json()["data"]["settings"]

        # Update registration_open
        update_resp = admin_client.put(
            "/api/v1/admin/settings",
            json={"key": "registration_open", "value": "true"}
        )
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["success"] is True
        assert data["data"]["key"] == "registration_open"

    def test_get_event_settings(self, admin_client):
        """Should get event-related settings."""
        response = admin_client.get("/api/v1/admin/settings")
        settings = response.json()["data"]["settings"]
        keys = [s["key"] for s in settings]

        # Verify event settings exist
        assert "event_date" in keys or "event_name" in keys or "event_venue" in keys


class TestAdminExport:
    """Test admin CSV export endpoint."""

    def test_export_delegates_csv(self, admin_client):
        """Should export delegates as CSV."""
        response = admin_client.get("/api/v1/admin/export/delegates")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        # Check filename header
        assert "delegates_export_" in response.headers["content-disposition"]


class TestAdminQueries:
    """Test admin queries management endpoints."""

    def test_list_queries(self, admin_client):
        """Should list queries with pagination."""
        response = admin_client.get("/api/v1/admin/queries?page=1&per_page=20")
        data = response.json()
        assert data["success"] is True
        assert "queries" in data["data"]
        assert "total" in data["data"]