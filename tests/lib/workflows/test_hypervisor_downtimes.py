import datetime
from unittest.mock import MagicMock, patch, call

from apis.icinga_api.enums.icinga_objects import IcingaObject
from apis.alertmanager_api.structs.alert_matcher_details import AlertMatcherDetails
from apis.alertmanager_api.structs.silence_details import SilenceDetails
from apis.icinga_api.structs.downtime_details import DowntimeDetails
import pytest
import pytz
from workflows.hypervisor_downtime import schedule_hypervisor_downtime
from workflows.hypervisor_downtime import (
    get_number_of_hours,
    _get_number_of_hours_from_absolute_datetime,
    _get_number_of_hours_from_duration,
)


# pylint:disable=too-many-locals
@pytest.mark.parametrize(
    "set_silence,set_downtime",
    [
        (True, False),
        (False, True),
        (True, True),
    ],
)
@pytest.mark.freeze_time
@patch("workflows.hypervisor_downtime.schedule_silence")
@patch("workflows.hypervisor_downtime.schedule_downtime")
def test_successful_schedule_hypervisor_downtime(
    mock_schedule_downtime,
    mock_schedule_silence,
    set_silence,
    set_downtime,
):
    """
    Test successful running of schedule hypervisor downtime
    """
    icinga_account = MagicMock()
    mock_hypervisor_name = "test_host"
    comment = f"starting downtime to patch and reboot host: {mock_hypervisor_name}"
    mock_start_time = datetime.datetime.now(pytz.utc)
    mock_input_end_time = ""
    mock_input_duration = "7h"
    mock_duration = get_number_of_hours(
        mock_start_time, mock_input_end_time, mock_input_duration
    )
    mock_end_time = mock_start_time + datetime.timedelta(hours=mock_duration)
    mock_start_timestamp = int(mock_start_time.timestamp())
    mock_end_timestamp = int(mock_end_time.timestamp())
    mock_silence_id = "mock ID"
    mock_schedule_silence.return_value = mock_silence_id
    alertmanager_account = MagicMock()
    schedule_hypervisor_downtime(
        icinga_account,
        alertmanager_account,
        hypervisor_name=mock_hypervisor_name,
        comment=comment,
        end_time=mock_input_end_time,
        duration=mock_input_duration,
        set_silence=set_silence,
        set_downtime=set_downtime,
    )
    mock_silence_details_instance = SilenceDetails(
        matchers=[AlertMatcherDetails(name="instance", value="test_host")],
        start_time_dt=mock_start_time,
        duration_hours=mock_duration,
        author="stackstorm",
        comment=comment,
    )
    mock_silence_details_hostname = SilenceDetails(
        matchers=[AlertMatcherDetails(name="hostname", value="test_host")],
        start_time_dt=mock_start_time,
        duration_hours=mock_duration,
        author="stackstorm",
        comment=comment,
    )
    if set_silence:
        mock_schedule_silence.assert_has_calls(
            [
                call(alertmanager_account, mock_silence_details_instance),
                call(alertmanager_account, mock_silence_details_hostname),
            ]
        )
    if set_downtime:
        mock_schedule_downtime.assert_called_once_with(
            icinga_account=icinga_account,
            details=DowntimeDetails(
                object_type=IcingaObject.HOST,
                object_name=mock_hypervisor_name,
                start_time=mock_start_timestamp,
                end_time=mock_end_timestamp,
                comment=comment,
                is_fixed=True,
                duration=mock_end_timestamp - mock_start_timestamp,
            ),
        )


@patch("workflows.hypervisor_downtime.schedule_silence")
@patch("workflows.hypervisor_downtime.schedule_downtime")
def test_unsuccessful_schedule_hypervisor_downtime(
    mock_schedule_downtime,
    mock_schedule_silence,
):
    """
    Test unsuccessful running of schedule hypervisor downtime -
    when either schedule silence raises an error
    """
    icinga_account = MagicMock()
    mock_hypervisor_name = "test_host"
    comment = f"starting downtime to patch and reboot host: {mock_hypervisor_name}"
    mock_duration = 7
    mock_schedule_silence.side_effect = Exception
    alertmanager_account = MagicMock()
    with pytest.raises(Exception):
        schedule_hypervisor_downtime(
            icinga_account,
            alertmanager_account,
            hypervisor_name=mock_hypervisor_name,
            comment=comment,
            duration_hours=mock_duration,
            set_silence=True,
            set_downtime=True,
        )

    mock_schedule_downtime.assert_not_called()


# ===============================================
# unit test function get_number_of_hours()
# ===============================================


def test_both_empty_strings_raise_exception():
    """Test that both empty strings raise ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, "", "")


def test_both_single_space_raise_exception():
    """Test that both parameters as single space raise ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, " ", " ")


def test_none_types_handled_too():
    """Test that both parameters as None in either field does not raise a ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "2024-01-01 11:00", None)
    assert result == 1

    result = get_number_of_hours(start_dt, None, "1h")
    assert result == 1


def test_both_multiple_spaces_raise_exception():
    """Test that both parameters as multiple spaces raise ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, "   ", "   ")


def test_both_tabs_and_spaces_raise_exception():
    """Test that both parameters as tabs and spaces raise ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, "\t  \t", "\t  \t")


def test_both_parameters_valid_raise_exception():
    """Test that providing both valid end_time_str and duration raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, "2024-01-01 15:00", "5d")


def test_both_parameters_with_spaces_valid_raise_exception():
    """Test that providing both valid parameters with spaces raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, "  2024-01-01 15:00  ", "  5d  ")


def test_invalid_endtime_input_raise_exception():
    """Test that an invalid input raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, "invalid", "")


def test_invalid_duration_input_raise_exception():
    """Test that an invalid input raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, "", "invalid")


def test_valid_absolute_datetime_same_day():
    """Test valid absolute datetime on the same day"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "2024-01-01 15:00", "")
    assert result == 5


def test_valid_absolute_datetime_next_day():
    """Test valid absolute datetime on the next day"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "2024-01-02 10:00", "")
    assert result == 24


def test_valid_absolute_datetime_with_leading_trailing_spaces():
    """Test valid absolute datetime with leading/trailing spaces"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "  2024-01-01 14:00  ", "")
    assert result == 4


def test_valid_absolute_datetime_duration_empty():
    """Test valid absolute datetime with empty duration parameter"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "2024-01-01 20:00", "")
    assert result == 10


def test_valid_duration_days_only():
    """Test valid duration with days only"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "", "5d")
    assert result == 120


def test_valid_duration_single_day():
    """Test valid duration with single day"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "", "1d")
    assert result == 24


def test_valid_duration_hours_only():
    """Test valid duration with hours only"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "", "12h")
    assert result == 12


def test_valid_duration_single_hour():
    """Test valid duration with single hour"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "", "1h")
    assert result == 1


def test_valid_duration_days_and_hours():
    """Test valid duration with both days and hours"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "", "5d 12h")
    assert result == 132


def test_valid_duration_hours_and_days_reversed():
    """Test valid duration with hours before days"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "", "12h 5d")
    assert result == 132


def test_valid_duration_case_insensitive():
    """Test that duration format is case insensitive"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "", "2D 6H")
    assert result == 54


def test_valid_duration_with_leading_trailing_spaces():
    """Test valid duration with leading/trailing spaces"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "", "  3d  ")
    assert result == 72


def test_valid_duration_end_time_empty():
    """Test valid duration with empty end_time_str parameter"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = get_number_of_hours(start_dt, "", "48h")
    assert result == 48


def test_empty_end_time_whitespace_duration():
    """Test empty end_time_str and whitespace duration"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, "", "   ")


def test_whitespace_end_time_empty_duration():
    """Test whitespace end_time_str and empty duration"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, "   ", "")


def test_invalid_absolute_datetime_format():
    """Test that invalid datetime format is caught by helper function"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    # This will be caught by get_number_of_hours_from_absolute_datetime
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, "2024-01-01", "")


def test_invalid_duration_format():
    """Test that invalid duration format is caught by helper function"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    # This will be caught by _get_number_of_hours_from_duration
    with pytest.raises(ValueError):
        get_number_of_hours(start_dt, "", "invalid")


# ===============================================
# unit test function _get_number_of_hours_from_absolute_datetime()
# ===============================================


def test_absolute_datetime_empty_string_raises_exception():
    """Test that an empty string raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "")


def test_absolute_datetime_invalid_format_no_time():
    """Test that date without time raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-01")


def test_absolute_datetime_invalid_format_wrong_separator():
    """Test that wrong separator (T instead of space) raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-01T10:00")


def test_absolute_datetime_invalid_format_wrong_date_separator():
    """Test that wrong date separator (slashes) raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "2024/01/01 10:00")


def test_absolute_datetime_invalid_format_random_text():
    """Test that random text raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "random text")


def test_absolute_datetime_invalid_month():
    """Test that invalid month raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "2024-13-01 10:00")


def test_absolute_datetime_invalid_day():
    """Test that invalid day raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-32 10:00")


def test_absolute_datetime_invalid_hour():
    """Test that invalid hour raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-01 25:00")


def test_absolute_datetime_invalid_minute():
    """Test that invalid minute raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-01 10:60")


def test_absolute_datetime_end_before_start():
    """Test that end time before start time raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-01 09:00")


def test_absolute_datetime_end_day_before_start():
    """Test that end date before start date raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-02 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-01 10:00")


def test_absolute_datetime_same_time():
    """Test that same start and end time raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-01 10:00")


def test_absolute_datetime_one_hour_later():
    """Test one hour difference"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-01 11:00")
    assert result == 1


def test_absolute_datetime_same_day_multiple_hours():
    """Test multiple hours on same day"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-01 15:00")
    assert result == 5


def test_absolute_datetime_exactly_one_day():
    """Test exactly 24 hours (one day)"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-02 10:00")
    assert result == 24


def test_absolute_datetime_multiple_days():
    """Test multiple days"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-05 10:00")
    assert result == 96


def test_absolute_datetime_days_and_hours():
    """Test combination of days and hours"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-03 14:00")
    assert result == 52


def test_absolute_datetime_across_month_boundary():
    """Test datetime across month boundary"""
    start_dt = datetime.datetime.strptime("2024-01-30 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours_from_absolute_datetime(start_dt, "2024-02-01 10:00")
    assert result == 48


def test_absolute_datetime_across_year_boundary():
    """Test datetime across year boundary"""
    start_dt = datetime.datetime.strptime("2024-12-31 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours_from_absolute_datetime(start_dt, "2025-01-01 10:00")
    assert result == 24


def test_absolute_datetime_with_minutes_rounds_down():
    """Test that minutes are truncated when converting to hours"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours_from_absolute_datetime(start_dt, "2024-01-01 11:59")
    assert result == 1


# ===============================================
# unit test function _get_number_of_hours_from_duration()
# ===============================================


def test_duration_empty_string_raises_exception():
    """Test that an empty string raises ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("")


def test_duration_single_space_raises_exception():
    """Test that a single space raises ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration(" ")


def test_duration_multiple_spaces_raises_exception():
    """Test that multiple spaces raise ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("   ")


def test_duration_tabs_and_spaces_raises_exception():
    """Test that tabs and spaces raise ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("\t  \t")


def test_duration_invalid_format_random_text():
    """Test that random text raises ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("random text")


def test_duration_invalid_format_only_number():
    """Test that a plain number without unit raises ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("123")


def test_duration_invalid_format_wrong_unit():
    """Test that invalid duration units raise ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("5m")


def test_duration_invalid_format_multiple_wrong_units():
    """Test that multiple invalid units raise ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("5m 30s")


def test_duration_invalid_format_datetime_string():
    """Test that datetime string raises ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("2024-01-01 10:00")


def test_duration_invalid_format_only_units_no_numbers():
    """Test that units without numbers raise ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("d h")


def test_duration_invalid_format_only_d():
    """Test that only 'd' without number raises ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("d")


def test_duration_invalid_format_only_h():
    """Test that only 'h' without number raises ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("h")


def test_duration_zero_days_zero_hours():
    """Test that 0d 0h raises ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("0d 0h")


def test_duration_zero_days_only():
    """Test that 0d raises ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("0d")


def test_duration_zero_hours_only():
    """Test that 0h raises ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("0h")


def test_invalid_format_negative_duration():
    """Test that negative duration raises ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("-5d")


def test_invalid_format_negative_hours():
    """Test that negative hours raise ValueError"""
    with pytest.raises(ValueError):
        _get_number_of_hours_from_duration("-12h")


def test_duration_single_day():
    """Test valid duration with single day"""
    result = _get_number_of_hours_from_duration("1d")
    assert result == 24


def test_duration_multiple_days():
    """Test valid duration with multiple days"""
    result = _get_number_of_hours_from_duration("5d")
    assert result == 120


def test_duration_single_hour():
    """Test valid duration with single hour"""
    result = _get_number_of_hours_from_duration("1h")
    assert result == 1


def test_duration_multiple_hours():
    """Test valid duration with multiple hours"""
    result = _get_number_of_hours_from_duration("12h")
    assert result == 12


def test_duration_twenty_four_hours():
    """Test valid duration with exactly 24 hours"""
    result = _get_number_of_hours_from_duration("24h")
    assert result == 24


def test_duration_days_and_hours():
    """Test valid duration with both days and hours"""
    result = _get_number_of_hours_from_duration("5d 12h")
    assert result == 132


def test_duration_hours_and_days_reversed():
    """Test valid duration with hours before days"""
    result = _get_number_of_hours_from_duration("12h 5d")
    assert result == 132


def test_duration_days_and_hours_multiple_spaces():
    """Test valid duration with multiple spaces between units"""
    result = _get_number_of_hours_from_duration("2d   6h")
    assert result == 54


def test_duration_days_and_hours_no_space():
    """Test valid duration with no space between units"""
    result = _get_number_of_hours_from_duration("2d6h")
    assert result == 54


def test_duration_case_insensitive_lowercase():
    """Test that duration format accepts lowercase units"""
    result = _get_number_of_hours_from_duration("2d 6h")
    assert result == 54


def test_duration_case_insensitive_uppercase():
    """Test that duration format accepts uppercase units"""
    result = _get_number_of_hours_from_duration("2D 6H")
    assert result == 54


def test_duration_case_insensitive_mixed_case():
    """Test that duration format accepts mixed case units"""
    result = _get_number_of_hours_from_duration("2D 6h")
    assert result == 54


def test_duration_large_number_of_days():
    """Test valid duration with large number of days"""
    result = _get_number_of_hours_from_duration("100d")
    assert result == 2400


def test_duration_large_number_of_hours():
    """Test valid duration with large number of hours"""
    result = _get_number_of_hours_from_duration("1000h")
    assert result == 1000


def test_duration_with_leading_spaces():
    """Test valid duration with leading spaces"""
    result = _get_number_of_hours_from_duration("  5d 12h")
    assert result == 132


def test_duration_with_trailing_spaces():
    """Test valid duration with trailing spaces"""
    result = _get_number_of_hours_from_duration("5d 12h  ")
    assert result == 132


def test_duration_with_leading_and_trailing_spaces():
    """Test valid duration with leading and trailing spaces"""
    result = _get_number_of_hours_from_duration("  5d 12h  ")
    assert result == 132


def test_duration_one_day_one_hour():
    """Test valid duration with one day and one hour"""
    result = _get_number_of_hours_from_duration("1d 1h")
    assert result == 25


def test_duration_ten_days():
    """Test valid duration with ten days"""
    result = _get_number_of_hours_from_duration("10d")
    assert result == 240
