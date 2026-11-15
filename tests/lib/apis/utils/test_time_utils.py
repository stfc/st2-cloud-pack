from datetime import datetime, timezone

import pytest

from apis.utils.time_utils import (
    timestamp_today,
    days_since_timestamp,
    parse_iso_utc,
    add_days_to_timestamp,
)


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


def test_add_positive_days():
    """Test adding a positive number of days to a timestamp."""
    assert add_days_to_timestamp("2026-01-10", 5) == "2026-01-15"


def test_add_negative_days():
    """Test subtracting days from a timestamp."""
    assert add_days_to_timestamp("2026-01-10", -5) == "2026-01-05"


def test_add_zero_days():
    """Test that adding zero days leaves the timestamp unchanged."""
    assert add_days_to_timestamp("2026-01-10", 0) == "2026-01-10"


def test_cross_month_boundary():
    """Test adding days across a month boundary."""
    assert add_days_to_timestamp("2026-01-30", 5) == "2026-02-04"


def test_cross_year_boundary():
    """Test adding days across a year boundary."""
    assert add_days_to_timestamp("2025-12-30", 5) == "2026-01-04"


def test_leap_year():
    """Test adding days across February 29 in a leap year."""
    assert add_days_to_timestamp("2024-02-28", 1) == "2024-02-29"
    assert add_days_to_timestamp("2024-02-28", 2) == "2024-03-01"


def test_non_leap_year():
    """Test adding days across February in a non-leap year."""
    assert add_days_to_timestamp("2025-02-28", 1) == "2025-03-01"


def test_subtract_across_year_boundary():
    """Test subtracting days across a year boundary."""
    assert add_days_to_timestamp("2026-01-02", -5) == "2025-12-28"


def test_large_number_of_days():
    """Test adding a large number of days."""
    assert add_days_to_timestamp("2026-01-01", 365) == "2027-01-01"


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-13-01",  # Invalid month
        "2026-02-30",  # Invalid day
        "2025-02-29",  # Invalid leap day
        "2026/01/10",  # Incorrect separator
        "invalid",  # Non-date string
        "",  # Empty string
    ],
)
def test_invalid_timestamp(timestamp):
    """Test that invalid timestamps raise a ValueError."""
    with pytest.raises(ValueError):
        add_days_to_timestamp(timestamp, 5)


@pytest.mark.parametrize(
    "timestamp, days, expected",
    [
        ("2026-01-01", 1, "2026-01-02"),
        ("2026-01-01", -1, "2025-12-31"),
        ("2026-06-15", 30, "2026-07-15"),
        ("2024-02-29", 365, "2025-02-28"),
        ("2026-12-31", 1, "2027-01-01"),
    ],
)
def test_add_days_parametrized(timestamp, days, expected):
    """Test multiple timestamp and day combinations."""
    assert add_days_to_timestamp(timestamp, days) == expected


def test_invalid_days_type():
    """Test that a non-integer days argument raises TypeError."""
    with pytest.raises(TypeError):
        add_days_to_timestamp("2026-01-10", "5")


def test_invalid_timestamp_type():
    """Test that a non-string timestamp raises TypeError."""
    with pytest.raises(TypeError):
        add_days_to_timestamp(None, 5)
