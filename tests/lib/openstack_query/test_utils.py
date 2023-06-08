import datetime

from unittest.mock import patch
from nose.tools import raises
from parameterized import parameterized

import openstack_query.utils as utils
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError


@parameterized(
    [
        (lambda a, b, c: None, ["a", "b", "c"]),
        (lambda a, b, c=1: None, ["a", "b"]),
        (lambda a, b, c=1: None, ["a", "b", "c"]),
        (lambda: None, []),
        (lambda a=1: None, []),
        (lambda a=1: None, ["a"]),
    ]
)
def test_check_filter_func_valid(func, args):
    assert utils.check_filter_func(func, args)


@parameterized(
    [
        (lambda a, b, c: None, []),
        (lambda a, b, c: None, ["a", "b"]),
        (lambda a=1: None, ["a", "b"]),
        (lambda a, b, c=1: None, ["c"]),
        (lambda: None, ["a"]),
    ]
)
@raises(TypeError)
def test_check_filter_func_mapping_invalid(func, args):
    assert utils.check_filter_func(func, args)


@parameterized([(10, 10), ("some-string", "some-string")])
def test_prop_equal_to_true(prop, value):
    assert utils.prop_equal_to(prop, value)


@parameterized([(10, 8), ("some-string", "some-other-string")])
def test_prop_equal_to_false(prop, value):
    assert not utils.prop_equal_to(prop, value)


def test_prop_less_than():
    assert utils.prop_less_than(8, 10)
    assert not utils.prop_less_than(10, 10)
    assert not utils.prop_less_than(10, 8)


def test_prop_not_less_than():
    assert utils.prop_greater_than(10, 8)
    assert not utils.prop_greater_than(10, 10)
    assert not utils.prop_greater_than(8, 10)


@parameterized(
    [
        # 1 day = 86400 seconds
        (1, 0, 0, 0, 86400),
        # 12 hours = 43200 seconds
        (0, 12, 0, 0, 43200),
        # 2 days, 30 minutes = 174600 seconds
        (2, 0, 30, 0, 174600),
        # 20 seconds
        (0, 0, 0, 20, 20),
    ]
)
@patch("openstack_query.utils.get_current_time")
def test_get_timestamp_in_seconds(
    days, hours, minutes, seconds, total_seconds, mock_current_datetime
):
    mock_current_datetime.return_value = datetime.datetime(2023, 6, 4, 10, 30, 0)
    out = utils.get_timestamp_in_seconds(days, hours, minutes, seconds)

    mock_current_datetime.assert_called_once()

    expected_timestamp = mock_current_datetime.return_value.timestamp() - total_seconds
    assert out == expected_timestamp


@raises(MissingMandatoryParamError)
def test_get_timestamp_in_seconds_invalid():
    utils.get_timestamp_in_seconds(days=0, hours=0, minutes=0, seconds=0)


@parameterized(
    [
        (
            1,
            0,
            0,
            0,
            "2023-06-04 10:30:00",
            "%Y-%m-%d %H:%M:%S",
            True,
        ),  # prop timestamp is older by 1 day
        (
            0,
            12,
            0,
            0,
            "2023-06-04 10:30:00 AM",
            "%Y-%m-%d %I:%M:%S %p",
            True,
        ),  # prop timestamp is older by 12 hours
        (
            1,
            0,
            0,
            0,
            "2023-06-02",
            "%Y-%m-%d",
            False,
        ),  # prop timestamp is younger by 1 day
        (
            0,
            0,
            30,
            0,
            "2023-06-04 10:00:00",
            "%Y-%m-%d %H:%M:%S",
            False,
        ),  # prop timestamp is equal
        (
            0,
            0,
            0,
            0.5,
            "2023-06-04 10:30:00",
            "%Y-%m-%d %H:%M:%S",
            True,
        ),  # prop timestamp is older by 0.5 seconds
    ]
)
@patch("openstack_query.utils.get_current_time")
def test_prop_older_than(
    days,
    hours,
    minutes,
    seconds,
    string_timestamp,
    timestamp_format,
    expected_out,
    mock_current_datetime,
):
    # sets a consistent specific datetime
    mock_current_datetime.return_value = datetime.datetime(2023, 6, 4, 10, 30, 0)

    out = utils.prop_older_than(
        prop=string_timestamp,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        prop_timestamp_fmt=timestamp_format,
    )
    assert out == expected_out


@parameterized(
    [
        (
            1,
            0,
            0,
            0,
            "2023-06-02 10:30:00",
            "%Y-%m-%d %H:%M:%S",
            True,
        ),  # prop timestamp is younger by 1 day
        (
            0,
            12,
            0,
            0,
            "2023-06-03 10:30:00 AM",
            "%Y-%m-%d %I:%M:%S %p",
            True,
        ),  # prop timestamp is younger by 12 hours
        (
            1,
            0,
            0,
            0,
            "2023-06-04",
            "%Y-%m-%d",
            False,
        ),  # prop timestamp is older by 1 day
        (
            0,
            0,
            30,
            0,
            "2023-06-04 10:00:00",
            "%Y-%m-%d %H:%M:%S",
            False,
        ),  # prop timestamp is equal
        (
            0,
            0,
            0,
            0.5,
            "2023-06-03 10:29:59",
            "%Y-%m-%d %H:%M:%S",
            True,
        ),  # prop timestamp is younger by .5 seconds
    ]
)
@patch("openstack_query.utils.get_current_time")
def test_prop_younger_than(
    days,
    hours,
    minutes,
    seconds,
    string_timestamp,
    timestamp_format,
    expected_out,
    mock_current_time,
):
    # sets a consistent specific datetime
    mock_current_time.return_value = datetime.datetime(2023, 6, 4, 10, 30, 0)

    out = utils.prop_younger_than(
        prop=string_timestamp,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        prop_timestamp_fmt=timestamp_format,
    )
    assert out == expected_out


@parameterized(
    [
        ("[0-9]+", "123", True),  # Numeric digits only
        ("[A-Za-z]+", "abc", True),  # Alphabetic characters only
        ("[A-Za-z]+", "123", False),  # No alphabetic characters
        ("[A-Za-z0-9]+", "abc123", True),  # Alphabetic and numeric characters
        ("[A-Za-z]+", "", False),  # Empty string, no match
    ]
)
def test_prop_matches_regex_valid(regex_string, test_prop, expected_out):
    out = utils.prop_matches_regex(test_prop, regex_string)
    assert out == expected_out


@parameterized(
    [
        (["val1", "val2", "val3"], "val1", True),
        (["val1", "val2"], "val3", False),
    ]
)
def test_prop_any_in(val_list, test_prop, expected_out):
    out = utils.prop_any_in(test_prop, val_list)
    assert out == expected_out


@raises(MissingMandatoryParamError)
def test_prop_any_in_empty_list():
    utils.prop_any_in("some-prop-val", [])


@parameterized(
    [
        (["val1", "val2", "val3"], "val1", False),
        (["val1", "val2"], "val3", True),
    ]
)
def test_prop_not_any_in(val_list, test_prop, expected_out):
    out = utils.prop_not_any_in(test_prop, val_list)
    assert out == expected_out
