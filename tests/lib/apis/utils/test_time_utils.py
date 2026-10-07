from datetime import datetime
import pytest
from apis.utils.time_utils import timestamp_today, days_since_timestamp


def test_timestamp_today():
    """Test that timestamp_today returns today's UTC date."""
    assert timestamp_today() == datetime.utcnow().strftime("%Y-%m-%d")


def test_days_since_timestamp():
    """Test that today's timestamp returns zero days elapsed."""
    assert days_since_timestamp(datetime.utcnow().strftime("%Y-%m-%d")) == 0


def test_days_since_timestamp_invalid_format():
    """Test that an invalid timestamp format raises ValueError."""
    with pytest.raises(ValueError, match="timestamp must have format YYYY-MM-DD"):
        days_since_timestamp("2026/10/07")
