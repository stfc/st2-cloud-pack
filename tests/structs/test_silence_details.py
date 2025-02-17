from datetime import timedelta, datetime
import pytest

from structs.alertmanager.alert_matcher_details import AlertMatcherDetails
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
    """
    test that SilenceDetails works when providing duration instead of end_time_dt
    Ensures that SilenceDetails correctly calculates end_time_dt based
    on the provided duration (duration_days, duration_hours, duration_minutes).
    Confirms that the calculated duration matches expectations.

    This test uses pytest.mark.parametrize,
    which allows us to run the same test with multiple sets of inputs.
    For each case:
        1. creates a SilenceDetails object with
           start_time_dt = "2025-02-05T14:00:00Z"
        2. uses the provided days, hours, and minutes to calculate end_time_dt
        3. checks:
            - start_time_str still is "2025-02-05T14:00:00Z"
            - end_time_str is the expected value
            - duration is the expect value
    """
    res = SilenceDetails(
        matchers=[AlertMatcherDetails(name="matcher1", value="foo")],
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


def test_matchers_raw():
    """test that matchers_raw provides dictionary of matcher info"""
    res = SilenceDetails(
        matchers=[AlertMatcherDetails(name="matcher1", value="foo")],
        author="author",
        comment="comment",
        start_time_dt=datetime(2025, 2, 5, 14, 00, 00, 486496),
        end_time_dt=datetime(2025, 2, 6, 14, 00, 00, 486496),
    )
    assert len(res.matchers_raw) == 1
    assert res.matchers_raw[0]["name"] == "matcher1"
    assert res.matchers_raw[0]["value"] == "foo"
    assert res.matchers_raw[0]["isEqual"] is True
    assert res.matchers_raw[0]["isRegex"] is False


def test_fail_end_time_older_than_start():
    """
    test that SilenceDetails fails when end time is before than start time
    tries to create a SilenceDetails object with:
        - start time = "2025-02-05T14:00:00Z"
        - a value of end time 1 year earlier
    and ensures an Excpetion is raised
    """
    with pytest.raises(ValueError):
        SilenceDetails(
            matchers=[AlertMatcherDetails(name="matcher1", value="foo")],
            author="author",
            comment="comment",
            start_time_dt=datetime(2025, 2, 5, 14, 00, 00, 486496),
            # 1 year previous - should fail
            end_time_dt=datetime(2024, 2, 5, 14, 00, 00, 486496),
        )


def test_fail_if_not_datetime():
    """
    test that SilenceDetails fails when end_time or start_time is not datetime
    It ensures an Exception is raised when one of them is not valid.
    Cases:
        - first case: end time is valid but start time is not
        - second case: start time is valid but end time is not
    """
    with pytest.raises(TypeError):
        SilenceDetails(
            matchers=[AlertMatcherDetails(name="matcher1", value="foo")],
            author="author",
            comment="comment",
            start_time_dt="foo",
            end_time_dt=datetime(2024, 2, 5, 14, 00, 00, 486496),
        )
    with pytest.raises(TypeError):
        SilenceDetails(
            matchers=[AlertMatcherDetails(name="matcher1", value="foo")],
            author="author",
            comment="comment",
            # start time not given
            start_time_dt=datetime(2024, 2, 5, 14, 00, 00, 486496),
            end_time_dt="foo",
        )


def test_fail_if_duration_and_end_time_not_given():
    """
    test that SilenceDetails fails if neither end_time or duration are provided

    It ensures an Exception is raised when a SilenceDetails object is created
    without any of the following parameters:
        - end time
        - duration (days)
        - duration (hours)
        - duration (minutes)
    """
    with pytest.raises(ValueError):
        SilenceDetails(
            matchers=[AlertMatcherDetails(name="matcher1", value="foo")],
            author="author",
            comment="comment",
            start_time_dt=datetime(2024, 2, 5, 14, 00, 00, 486496),
            # end time and duration are not given
        )
