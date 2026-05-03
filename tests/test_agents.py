"""Tests for agent modules."""
import pytest
from pathlib import Path


class TestConfig:
    """Tests for config loading."""

    def test_load_config(self, config):
        """Test config.yaml loads correctly with env var resolution."""
        assert config is not None
        assert "agent" in config
        assert "model" in config["agent"]

    def test_agent_config_has_api_key(self, config):
        """Test agent config has api_key field."""
        agent = config.get("agent", {})
        assert "api_key" in agent


class TestCollectorAgent:
    """Tests for CollectorAgent."""

    def test_create(self, config):
        """Test creating a CollectorAgent."""
        from agents.collector import CollectorAgent
        agent = CollectorAgent(config)
        assert agent is not None

    def test_collect(self, config):
        """Test CollectorAgent.collect() returns reports."""
        from agents.collector import CollectorAgent
        from models.report import DailyReport
        agent = CollectorAgent(config)
        results = agent.collect("2026-04-29")
        assert isinstance(results, list)
        if results:
            assert all(isinstance(r, DailyReport) for r in results)


class TestAnalyzerAgent:
    """Tests for AnalyzerAgent."""

    def test_create(self, config):
        """Test creating an AnalyzerAgent."""
        from agents.analyzer import AnalyzerAgent
        agent = AnalyzerAgent(config)
        assert agent is not None

    def test_build_analysis_prompt(self, config, sample_report):
        """Test _build_analysis_prompt returns a non-empty string."""
        from agents.analyzer import AnalyzerAgent
        agent = AnalyzerAgent(config)
        prompt = agent._build_analysis_prompt(sample_report)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert sample_report.reporter in prompt

    def test_safe_json_parse_normal(self, config):
        """Test _safe_json_parse with plain JSON."""
        from agents.analyzer import AnalyzerAgent
        agent = AnalyzerAgent(config)
        result = agent._safe_json_parse('{"a":1}')
        assert result == {"a": 1}

    def test_safe_json_parse_markdown(self, config):
        """Test _safe_json_parse with markdown code block."""
        from agents.analyzer import AnalyzerAgent
        agent = AnalyzerAgent(config)
        result = agent._safe_json_parse('```json\n{"b":2}\n```')
        assert result == {"b": 2}

    def test_safe_json_parse_invalid(self, config):
        """Test _safe_json_parse returns empty dict on invalid input."""
        from agents.analyzer import AnalyzerAgent
        agent = AnalyzerAgent(config)
        result = agent._safe_json_parse("not json at all")
        assert result == {}


class TestAlertAgent:
    """Tests for AlertAgent."""

    def test_create(self, config):
        """Test creating an AlertAgent."""
        from agents.alert_agent import AlertAgent
        agent = AlertAgent(config)
        assert agent is not None

    def test_check(self, config, mixed_analyses):
        """Test alert_agent.check() detects risks."""
        from agents.alert_agent import AlertAgent
        from models.alert import Alert
        agent = AlertAgent(config)
        alerts = agent.check(mixed_analyses)
        assert isinstance(alerts, list)
        assert len(alerts) > 0
        assert all(isinstance(a, Alert) for a in alerts)

    def test_team_anomaly_detection(self, config):
        """Test team anomaly detection with all negative members."""
        from agents.alert_agent import AlertAgent
        from models.report import ReportAnalysis
        agent = AlertAgent(config)
        negative_analyses = [
            ReportAnalysis(
                reporter=f"U{i}", date="2026-04-29", content="Neg",
                sentiment="negative", risk_level="high",
                keywords=[], risks=["Issue"], suggestions=[], achievements=[],
            )
            for i in range(3)
        ]
        result = agent._check_team_anomaly(negative_analyses)
        assert result is not None

    def test_team_anomaly_no_issue(self, config):
        """Test team anomaly detection with all positive members."""
        from agents.alert_agent import AlertAgent
        from models.report import ReportAnalysis
        agent = AlertAgent(config)
        positive_analyses = [
            ReportAnalysis(
                reporter=f"U{i}", date="2026-04-29", content="Good",
                sentiment="positive", risk_level="low",
                keywords=[], risks=[], suggestions=[], achievements=[],
            )
            for i in range(3)
        ]
        result = agent._check_team_anomaly(positive_analyses)
        assert result is None

    def test_team_anomaly_too_few(self, config):
        """Test team anomaly with fewer than 3 members returns None."""
        from agents.alert_agent import AlertAgent
        from models.report import ReportAnalysis
        agent = AlertAgent(config)
        few_analyses = [
            ReportAnalysis(
                reporter="X", date="2026-04-29", content="Neg",
                sentiment="negative", risk_level="high",
                keywords=[], risks=[], suggestions=[], achievements=[],
            )
        ]
        result = agent._check_team_anomaly(few_analyses)
        assert result is None


class TestReporterAgent:
    """Tests for ReporterAgent."""

    def test_create(self, config):
        """Test creating a ReporterAgent."""
        from agents.reporter import ReporterAgent
        agent = ReporterAgent(config)
        assert agent is not None

    def test_generate_daily(self, config, project_root):
        """Test generate() creates a daily report file."""
        from agents.reporter import ReporterAgent
        from models.report import ReportAnalysis
        agent = ReporterAgent(config)
        test_analyses = [
            ReportAnalysis(
                reporter="Test", date="2026-04-29", content="Test",
                sentiment="positive", risk_level="low",
                keywords=["test"], risks=[], suggestions=[], achievements=[],
            )
        ]
        path = agent.generate(test_analyses, "2026-04-29-test")
        assert path is not None
        assert Path(path).exists()

    def test_generate_weekly(self, config, project_root):
        """Test generate_weekly() creates a file."""
        from agents.reporter import ReporterAgent
        agent = ReporterAgent(config)
        path = agent.generate_weekly()
        if path is not None:
            assert Path(path).exists()

    def test_generate_monthly(self, config, project_root):
        """Test generate_monthly() creates a file."""
        from agents.reporter import ReporterAgent
        agent = ReporterAgent(config)
        path = agent.generate_monthly()
        if path is not None:
            assert Path(path).exists()
