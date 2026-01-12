import datetime
from unittest.mock import MagicMock, patch, call

from apis.icinga_api.enums.icinga_objects import IcingaObject
from apis.alertmanager_api.structs.alert_matcher_details import AlertMatcherDetails
from apis.alertmanager_api.structs.silence_details import SilenceDetails
from apis.icinga_api.structs.downtime_details import DowntimeDetails
import pytest
import pytz
from workflows.hypervisor_downtime import schedule_hypervisor_downtime
from workflows.hypervisor_downtime import _get_number_of_hours


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
    mock_input_end_time = "7h"
    mock_duration = _get_number_of_hours(mock_start_time, mock_input_end_time)
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
# unit test function _get_number_of_hours()
# ===============================================


def test_empty_string_raises_exception():
    """Test that an empty string raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours(start_dt, "")


def test_single_space_raises_exception():
    """Test that a single space raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours(start_dt, " ")


def test_multiple_spaces_raises_exception():
    """Test that multiple spaces raise ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours(start_dt, "   ")


def test_tabs_and_spaces_raises_exception():
    """Test that tabs and spaces raise ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours(start_dt, "\t  \t")


def test_invalid_format_random_text():
    """Test that random text raises ValueError with appropriate message"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours(start_dt, "random text")


def test_invalid_format_incomplete_datetime():
    """Test that incomplete datetime.datetime format raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours(start_dt, "2024-01-01")


def test_invalid_format_wrong_datetime_separator():
    """Test that wrong datetime.datetime separator raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours(start_dt, "2024-01-01T10:00")


def test_invalid_format_only_number():
    """Test that a plain number raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours(start_dt, "123")


def test_invalid_format_invalid_duration_unit():
    """Test that invalid duration unit raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours(start_dt, "5m 12s")


def test_invalid_format_negative_duration():
    """Test that negative duration raises ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours(start_dt, "-5d")


def test_invalid_format_negative_hours():
    """Test that negative hours raise ValueError"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    with pytest.raises(ValueError):
        _get_number_of_hours(start_dt, "-12h")


def test_valid_absolute_datetime_same_day():
    """Test valid absolute datetime.datetime on the same day"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours(start_dt, "2024-01-01 15:00")
    assert result == 5


def test_valid_absolute_datetime_next_day():
    """Test valid absolute datetime.datetime on the next day"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours(start_dt, "2024-01-02 10:00")
    assert result == 24


def test_valid_absolute_datetime_with_leading_spaces():
    """Test valid absolute datetime.datetime with leading/trailing spaces"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours(start_dt, "  2024-01-01 14:00  ")
    assert result == 4


def test_valid_duration_days_only():
    """Test valid duration with days only"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours(start_dt, "5d")
    assert result == 120


def test_valid_duration_single_day():
    """Test valid duration with single day"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours(start_dt, "1d")
    assert result == 24


def test_valid_duration_hours_only():
    """Test valid duration with hours only"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours(start_dt, "12h")
    assert result == 12


def test_valid_duration_single_hour():
    """Test valid duration with single hour"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours(start_dt, "1h")
    assert result == 1


def test_valid_duration_days_and_hours():
    """Test valid duration with both days and hours"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours(start_dt, "5d 12h")
    assert result == 132


def test_valid_duration_hours_and_days_reversed():
    """Test valid duration with hours before days"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours(start_dt, "12h 5d")
    assert result == 132


def test_valid_duration_case_insensitive():
    """Test that duration format is case insensitive"""
    start_dt = datetime.datetime.strptime("2024-01-01 10:00", "%Y-%m-%d %H:%M").replace(
        tzinfo=pytz.utc
    )
    result = _get_number_of_hours(start_dt, "2D 6H")
    assert result == 54
