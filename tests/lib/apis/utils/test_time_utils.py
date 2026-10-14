from datetime import datetime, timezone

import pytest

from apis.utils.time_utils import timestamp_today, days_since_timestamp, parse_iso_utc


def test_parse_iso_utc_z_suffix():
    """
    Tests a timestamp with a Z suffix is parsed as UTC
    """
    assert parse_iso_utc("2026-09-04T09:10:48Z") == datetime(
        2026, 9, 4, 9, 10, 48, tzinfo=timezone.utc
    )


def test_parse_iso_utc_offset():
    """
    Tests an explicit UTC offset is converted to UTC
    """
    assert parse_iso_utc("2026-09-04T11:10:48+02:00") == datetime(
        2026, 9, 4, 9, 10, 48, tzinfo=timezone.utc
    )


def test_parse_iso_utc_naive():
    """
    Tests a naive timestamp (Nova's instance action start times) is
    assumed to be UTC
    """
    assert parse_iso_utc("2026-09-04T09:10:48.000000") == datetime(
        2026, 9, 4, 9, 10, 48, tzinfo=timezone.utc
    )


def test_parse_iso_utc_raises_on_garbage():
    """
    Tests an unparseable value raises ValueError
    """
    with pytest.raises(ValueError):
        parse_iso_utc("not a timestamp")


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
