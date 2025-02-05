from datetime import timedelta, datetime
import pytest
from structs.alertmanager.silence_details import SilenceDetails


@pytest.mark.parametrize(
    "days,hours,minutes,expected_end_time_str,expected_time_delta",
    [
        (1, 1, 10, "2025-02-06T15:10:00Z", timedelta(days=1, seconds=4200)),
        (2, 0, 0, "2025-02-07T14:00:00Z", timedelta(days=2, seconds=0)),
        (0, 2, 0, "2025-02-05T16:00:00Z", timedelta(days=0, seconds=7200)),
        (0, 0, 20, "2025-02-05T14:20:00Z", timedelta(days=0, seconds=1200)),
    ],
)
def test_duration_calc(
    days, hours, minutes, expected_end_time_str, expected_time_delta
):
    """test that SilenceDetails works when providing duration instead of end_time_dt"""
    res = SilenceDetails(
        matchers=["matcher1"],
        author="author",
        comment="comment",
        start_time_dt=datetime(2025, 2, 5, 14, 00, 00, 486496),
        end_time_dt=None,
        duration_days=days,
        duration_hours=hours,
        duration_minutes=minutes,
    )
    assert res.start_time_str == "2025-02-05T14:00:00Z"
    assert res.end_time_str == expected_end_time_str
    assert res.duration == expected_time_delta


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
