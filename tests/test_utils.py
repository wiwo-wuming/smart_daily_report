"""Tests for utils module."""
import pytest
from datetime import datetime


class TestUtilsImports:
    """Test utils module imports."""

    def test_import_utils_package(self):
        """Test importing the utils package."""
        from utils import LLMClient, format_date, ensure_dir
        assert LLMClient is not None
        assert callable(format_date)
        assert callable(ensure_dir)

    def test_import_helpers(self):
        """Test importing helper functions."""
        from utils.helpers import parse_date, get_date_range, truncate_text
        assert callable(parse_date)
        assert callable(get_date_range)
        assert callable(truncate_text)


class TestFormatDate:
    """Tests for format_date function."""

    def test_format_date_default(self):
        """Test format_date with default args returns today's date."""
        from utils.helpers import format_date
        result = format_date()
        today = datetime.now().strftime("%Y-%m-%d")
        assert result == today

    def test_format_date_custom(self):
        """Test format_date with a custom date string."""
        from utils.helpers import format_date
        result = format_date("2026-05-01", "%Y-%m-%d")
        assert result == "2026-05-01"


class TestParseDate:
    """Tests for parse_date function."""

    def test_parse_date_hyphen(self):
        """Test parse_date with YYYY-MM-DD format."""
        from utils.helpers import parse_date
        result = parse_date("2026-04-29")
        assert isinstance(result, datetime)
        assert result.year == 2026
        assert result.month == 4
        assert result.day == 29

    def test_parse_date_slash(self):
        """Test parse_date with YYYY/MM/DD format."""
        from utils.helpers import parse_date
        result = parse_date("2026/04/29")
        assert result.year == 2026
        assert result.month == 4
        assert result.day == 29

    def test_parse_date_compact(self):
        """Test parse_date with YYYYMMDD format."""
        from utils.helpers import parse_date
        result = parse_date("20260429")
        assert result.year == 2026

    def test_parse_date_invalid(self):
        """Test parse_date raises ValueError on invalid input."""
        from utils.helpers import parse_date
        with pytest.raises(ValueError):
            parse_date("not-a-date")


class TestTruncateText:
    """Tests for truncate_text function."""

    def test_truncate_short_text(self):
        """Test truncate_text with text shorter than max_length."""
        from utils.helpers import truncate_text
        result = truncate_text("hello", max_length=10)
        assert result == "hello"

    def test_truncate_long_text(self):
        """Test truncate_text with text longer than max_length."""
        from utils.helpers import truncate_text
        result = truncate_text("hello world this is a long text", max_length=10)
        assert len(result) <= 13  # 10 + "..." = 13 max
        assert result.endswith("...")


class TestGetDateRange:
    """Tests for get_date_range function."""

    def test_get_date_range(self):
        """Test get_date_range returns all dates in range."""
        from utils.helpers import get_date_range
        dates = get_date_range("2026-04-01", "2026-04-03")
        assert dates == ["2026-04-01", "2026-04-02", "2026-04-03"]

    def test_get_date_range_single_day(self):
        """Test get_date_range with same start and end."""
        from utils.helpers import get_date_range
        dates = get_date_range("2026-04-01", "2026-04-01")
        assert dates == ["2026-04-01"]
