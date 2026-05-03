"""Tests for data models."""
import pytest


class TestModelImports:
    """Test model imports."""

    def test_import_models(self):
        """Test importing models package."""
        from models import DailyReport, ReportAnalysis, Alert
        assert DailyReport is not None
        assert ReportAnalysis is not None
        assert Alert is not None


class TestDailyReport:
    """Tests for DailyReport dataclass."""

    def test_create(self):
        """Test creating a DailyReport instance."""
        from models.report import DailyReport
        report = DailyReport(
            reporter="Test", date="2026-04-29",
            content="Test content", source="test",
        )
        assert report.reporter == "Test"
        assert report.date == "2026-04-29"
        assert report.content == "Test content"
        assert report.source == "test"

    def test_defaults(self):
        """Test DailyReport default values."""
        from models.report import DailyReport
        report = DailyReport(reporter="X", date="2026-01-01", content="Y")
        assert report.source == "unknown"
        assert report.record_id == ""

    def test_attrs_exist(self):
        """Test DailyReport has all expected attributes."""
        from models.report import DailyReport
        report = DailyReport(reporter="X", date="2026-01-01", content="Y")
        assert hasattr(report, "reporter")
        assert hasattr(report, "content")
        assert hasattr(report, "source")
        assert hasattr(report, "date")
        assert hasattr(report, "record_id")


class TestReportAnalysis:
    """Tests for ReportAnalysis dataclass."""

    def test_create(self):
        """Test creating a ReportAnalysis instance."""
        from models.report import ReportAnalysis
        analysis = ReportAnalysis(
            reporter="Test", date="2026-04-29", content="Test",
            keywords=["key1"], sentiment="positive", risk_level="low",
            risks=[], suggestions=[], achievements=[],
            raw_analysis={"summary": "test summary"},
        )
        assert analysis.reporter == "Test"
        assert analysis.sentiment == "positive"
        assert analysis.risk_level == "low"

    def test_summary_from_raw(self):
        """Test summary defaults to empty; raw_analysis is preserved."""
        from models.report import ReportAnalysis
        analysis = ReportAnalysis(
            reporter="Test", date="2026-04-29", content="Test",
            raw_analysis={"summary": "auto summary"},
        )
        # summary field default is ""; __post_init__ only overrides if None
        assert analysis.summary == ""
        assert analysis.raw_analysis["summary"] == "auto summary"

    def test_defaults(self):
        """Test ReportAnalysis default values."""
        from models.report import ReportAnalysis
        analysis = ReportAnalysis(
            reporter="X", date="2026-01-01", content="Y",
        )
        assert analysis.sentiment == "neutral"
        assert analysis.risk_level == "low"
        assert analysis.keywords == []
        assert analysis.risks == []

    def test_attrs_exist(self):
        """Test ReportAnalysis has all expected attributes."""
        from models.report import ReportAnalysis
        analysis = ReportAnalysis(reporter="X", date="2026-01-01", content="Y")
        assert hasattr(analysis, "sentiment")
        assert hasattr(analysis, "risk_level")
        assert hasattr(analysis, "keywords")
        assert hasattr(analysis, "risks")
        assert hasattr(analysis, "suggestions")
        assert hasattr(analysis, "achievements")


class TestAlert:
    """Tests for Alert dataclass."""

    def test_create(self):
        """Test creating an Alert instance."""
        from models.alert import Alert
        alert = Alert(
            alert_type="individual", level="high", title="Test Alert",
            content="Test content", affected_members=["Zhang San"],
            suggestions=["Suggestion 1"],
        )
        assert alert.alert_type == "individual"
        assert alert.level == "high"
        assert alert.title == "Test Alert"
        assert alert.content == "Test content"
        assert alert.affected_members == ["Zhang San"]
        assert alert.suggestions == ["Suggestion 1"]

    def test_created_at_auto(self):
        """Test created_at is auto-generated."""
        from models.alert import Alert
        alert = Alert(
            alert_type="individual", level="low",
            title="Test", content="Test",
        )
        assert alert.created_at is not None
        assert len(alert.created_at) > 0

    def test_defaults(self):
        """Test Alert default values."""
        from models.alert import Alert
        alert = Alert(
            alert_type="individual", level="low",
            title="Test", content="Test",
        )
        assert alert.alert_id == ""
        assert alert.status == "pending"

    def test_attrs_exist(self):
        """Test Alert has all expected attributes."""
        from models.alert import Alert
        alert = Alert(
            alert_type="individual", level="low",
            title="Test", content="Test",
        )
        assert hasattr(alert, "alert_type")
        assert hasattr(alert, "level")
        assert hasattr(alert, "affected_members")
        assert hasattr(alert, "suggestions")
        assert hasattr(alert, "created_at")
        assert hasattr(alert, "status")
