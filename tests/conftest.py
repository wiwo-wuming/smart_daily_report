"""pytest fixtures for smart_daily_report tests."""
import os
import sys
from pathlib import Path

import yaml
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.helpers import resolve_env_vars


@pytest.fixture(scope="session")
def project_root():
    """Return the project root path."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def raw_config(project_root):
    """Load raw config.yaml without env var resolution."""
    config_file = project_root / "config.yaml"
    with open(config_file, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def config(raw_config):
    """Load config with env var resolution."""
    return resolve_env_vars(raw_config)


@pytest.fixture
def sample_report():
    """Create a sample DailyReport for testing."""
    from models.report import DailyReport
    return DailyReport(
        reporter="TestUser",
        date="2026-04-29",
        content="Completed development of API module, fixed 3 bugs",
        source="test",
    )


@pytest.fixture
def sample_analysis(sample_report):
    """Create a sample ReportAnalysis for testing."""
    from models.report import ReportAnalysis
    return ReportAnalysis(
        reporter=sample_report.reporter,
        date=sample_report.date,
        content=sample_report.content,
        keywords=["API", "bugfix"],
        sentiment="positive",
        risk_level="low",
        risks=[],
        suggestions=["Keep up the good work"],
        achievements=["API module completed"],
        raw_analysis={"summary": "Completed API development and bug fixes"},
    )


@pytest.fixture
def sample_alert():
    """Create a sample Alert for testing."""
    from models.alert import Alert
    return Alert(
        alert_type="individual",
        level="high",
        title="Test Alert",
        content="Test alert content",
        affected_members=["Zhang San"],
        suggestions=["Investigate immediately"],
    )


@pytest.fixture
def mixed_analyses():
    """Create mixed analyses (positive + negative) for alert testing."""
    from models.report import ReportAnalysis
    return [
        ReportAnalysis(
            reporter="A", date="2026-04-29", content="Normal work",
            sentiment="positive", risk_level="low",
            keywords=[], risks=[], suggestions=[], achievements=[],
        ),
        ReportAnalysis(
            reporter="B", date="2026-04-29", content="Serious issue found",
            sentiment="negative", risk_level="high",
            keywords=[], risks=["Serious issue"], suggestions=["Fix now"], achievements=[],
        ),
        ReportAnalysis(
            reporter="C", date="2026-04-29", content="Regular update",
            sentiment="neutral", risk_level="low",
            keywords=[], risks=[], suggestions=[], achievements=[],
        ),
    ]
