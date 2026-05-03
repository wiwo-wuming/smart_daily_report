"""Tests for services module."""
import pytest


class TestDataSource:
    """Tests for DataSource abstract base class."""

    def test_abc_exists(self):
        """Test DataSource ABC can be imported."""
        from services.data_source import DataSource
        assert DataSource is not None

    def test_abc_is_abstract(self):
        """Test DataSource is abstract (cannot instantiate directly)."""
        from services.data_source import DataSource
        with pytest.raises(TypeError):
            DataSource()  # type: ignore[abstract]


class TestJSONClient:
    """Tests for JSONClient."""

    def test_create(self, project_root):
        """Test creating a JSONClient instance."""
        from services.json_client import JSONClient
        client = JSONClient(str(project_root / "data" / "sample_reports.json"))
        assert client is not None

    def test_fetch_reports(self, project_root):
        """Test JSONClient.fetch_reports returns data."""
        from services.json_client import JSONClient
        client = JSONClient(str(project_root / "data" / "sample_reports.json"))
        results = client.fetch_reports("2026-04-29")
        assert results is not None


class TestExcelClient:
    """Tests for ExcelClient."""

    def test_create(self, project_root):
        """Test creating an ExcelClient instance."""
        from services.excel_client import ExcelClient
        client = ExcelClient(str(project_root / "data" / "daily_reports.csv"))
        assert client is not None


class TestFeishuClient:
    """Tests for FeishuClient."""

    def test_create(self):
        """Test creating a FeishuClient instance."""
        from services.feishu_client import FeishuClient
        client = FeishuClient({
            "app_id": "test_id",
            "app_secret": "test_secret",
            "app_token": "test_token",
            "table_id": "test_table",
        })
        assert client is not None


class TestNotificationService:
    """Tests for NotificationService."""

    def test_create(self):
        """Test creating a NotificationService instance."""
        from services.notification import NotificationService
        svc = NotificationService({"enabled": False})
        assert svc is not None

    def test_send_disabled_mode(self, sample_alert):
        """Test send() in disabled mode does not raise."""
        from services.notification import NotificationService
        svc = NotificationService({"enabled": False})
        # Should not raise exception
        result = svc.send(sample_alert)
        assert result is None
