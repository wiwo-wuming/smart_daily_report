"""Tests for Flask dashboard."""
import json
import pytest


class TestDashboard:
    """Tests for the Flask dashboard app."""

    def test_app_exists(self):
        """Test Flask app can be imported."""
        from dashboard import app
        assert app is not None

    def test_get_index(self):
        """Test GET / returns 200."""
        from dashboard import app
        with app.test_client() as client:
            resp = client.get("/")
            assert resp.status_code == 200

    def test_html_contains_chartjs(self):
        """Test index page includes Chart.js CDN."""
        from dashboard import app
        with app.test_client() as client:
            resp = client.get("/")
            assert b"chart.js" in resp.data

    def test_html_contains_dashboard(self):
        """Test index page includes dashboard element."""
        from dashboard import app
        with app.test_client() as client:
            resp = client.get("/")
            assert b"dashboard" in resp.data

    def test_get_api_dashboard(self):
        """Test GET /api/dashboard returns 200 and valid JSON."""
        from dashboard import app
        with app.test_client() as client:
            resp = client.get("/api/dashboard")
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert "stats" in data
            assert "trends" in data
            assert "members" in data
            assert "alerts" in data
            assert "member_activity" in data

    def test_api_has_stats(self):
        """Test API response has stats with total_reports."""
        from dashboard import app
        with app.test_client() as client:
            resp = client.get("/api/dashboard")
            data = json.loads(resp.data)
            assert "total_reports" in data["stats"]

    def test_api_has_trends(self):
        """Test API response has trends data."""
        from dashboard import app
        with app.test_client() as client:
            resp = client.get("/api/dashboard")
            data = json.loads(resp.data)
            assert isinstance(data["trends"], list)

    def test_api_has_members(self):
        """Test API response has members key."""
        from dashboard import app
        with app.test_client() as client:
            resp = client.get("/api/dashboard")
            data = json.loads(resp.data)
            assert "members" in data

    def test_api_has_alerts(self):
        """Test API response has alerts key."""
        from dashboard import app
        with app.test_client() as client:
            resp = client.get("/api/dashboard")
            data = json.loads(resp.data)
            assert "alerts" in data

    def test_api_has_member_activity(self):
        """Test API response has member_activity key."""
        from dashboard import app
        with app.test_client() as client:
            resp = client.get("/api/dashboard")
            data = json.loads(resp.data)
            assert "member_activity" in data
