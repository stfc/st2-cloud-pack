import datetime
from unittest.mock import MagicMock, patch, call

from enums.icinga.icinga_objects import IcingaObject
from structs.alertmanager.alert_matcher_details import AlertMatcherDetails
from structs.alertmanager.silence_details import SilenceDetails
from structs.icinga.downtime_details import DowntimeDetails
from workflows.hypervisor_downtime import schedule_hypervisor_downtime
import pytest

import pytz


@pytest.mark.freeze_time
@patch("workflows.hypervisor_downtime.schedule_silence")
@patch("workflows.hypervisor_downtime.schedule_downtime")
def test_successful_schedule_hypervisor_downtime(
    mock_schedule_downtime,
    mock_schedule_silence,
):
    """
    Test successful running of schedule hypervisor downtime
    """
    icinga_account = MagicMock()
    mock_hypervisor_name = "test_host"
    comment = f"starting downtime to patch and reboot host: {mock_hypervisor_name}"
    mock_duration = 7
    mock_start_time = datetime.datetime.now(pytz.utc)
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
        duration_hours=mock_duration,
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
    mock_schedule_silence.assert_has_calls(
        [
            call(alertmanager_account, mock_silence_details_instance),
            call(alertmanager_account, mock_silence_details_hostname),
        ]
    )
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
        )

    mock_schedule_downtime.assert_not_called()
