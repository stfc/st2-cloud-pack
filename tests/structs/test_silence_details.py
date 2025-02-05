import pytest
from datetime import timedelta, datetime
from structs.alertmanager.silence_details import SilenceDetails


def test_duration_calc():
    """test that SilenceDetails works when providing duration instead of end_time_dt"""
    res = SilenceDetails(
        matchers=["matcher1"],
        author="author",
        comment="comment",
        start_time_dt=datetime(2025, 2, 5, 14, 00, 00, 486496),
        end_time_dt=None,
        duration_days=1,
        duration_hours=1,
        duration_minutes=10,
    )
    assert res.start_time_str == "2025-02-05T14:00:00Z"
    # 1 day, 1 hour, 10 minutes from start time
    assert res.end_time_str == "2025-02-06T15:10:00Z"
    assert res.duration == timedelta(days=1, seconds=4200)


def test_fail_end_time_older_than_start():
    """test that SilenceDetails fails when end time is older than start time"""
    with pytest.raises(ValueError):
        SilenceDetails(
            matchers=["matcher1"],
            author="author",
            comment="comment",
            start_time_dt=datetime(2025, 2, 5, 14, 00, 00, 486496),
            # 1 year previous - should fail
            end_time_dt=datetime(2024, 2, 5, 14, 00, 00, 486496),
        )


def test_fail_if_not_datetime():
    """test that SilenceDetails fails when end_time or start_time is not datetime"""
    with pytest.raises(TypeError):
        SilenceDetails(
            matchers=["matcher1"],
            author="author",
            comment="comment",
            start_time_dt="foo",
            end_time_dt=datetime(2024, 2, 5, 14, 00, 00, 486496),
        )
    with pytest.raises(TypeError):
        SilenceDetails(
            matchers=["matcher1"],
            author="author",
            comment="comment",
            # start time not given
            start_time_dt=datetime(2024, 2, 5, 14, 00, 00, 486496),
            end_time_dt="foo",
        )


def test_fail_if_duration_and_end_time_not_given():
    """
    test that SilenceDetails fails if neither end_time or duration are provided
    """
    with pytest.raises(ValueError):
        SilenceDetails(
            matchers=["matcher1"],
            author="author",
            comment="comment",
            start_time_dt=datetime(2024, 2, 5, 14, 00, 00, 486496),
            # end time and duration are not given
        )
