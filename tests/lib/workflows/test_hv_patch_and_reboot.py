import datetime
from unittest.mock import MagicMock, patch, call
from paramiko import SSHException

from enums.icinga.icinga_objects import IcingaObject
from structs.alertmanager.alert_matcher_details import AlertMatcherDetails
from structs.alertmanager.silence_details import SilenceDetails
from structs.icinga.downtime_details import DowntimeDetails
from structs.ssh.ssh_connection_details import SSHDetails
from workflows.hv_patch_and_reboot import patch_and_reboot
import pytest


# pylint:disable=too-many-locals
@pytest.mark.freeze_time
@patch("workflows.hv_patch_and_reboot.schedule_silence")
@patch("workflows.hv_patch_and_reboot.schedule_downtime")
@patch("workflows.hv_patch_and_reboot.SSHConnection")
def test_successful_patch_and_reboot(
    mock_ssh_conn,
    mock_schedule_downtime,
    mock_schedule_silence,
):
    """
    Test successful running of patch and reboot workflow
    """
    icinga_account = MagicMock()
    mock_ssh_conn.return_value.run_command_on_host.side_effect = [
        str.encode("Patch command output"),
        str.encode("Reboot command output"),
    ]
    mock_hypervisor_name = "test_host"
    comment = f"starting downtime to patch and reboot host: {mock_hypervisor_name}"
    mock_private_key_path = "/home/stackstorm/.ssh/id_rsa"
    mock_start_time = datetime.datetime.utcnow()
    mock_end_time = mock_start_time + datetime.timedelta(hours=6)
    mock_start_timestamp = int(mock_start_time.timestamp())
    mock_end_timestamp = int(mock_end_time.timestamp())
    mock_silence_id = "mock ID"
    mock_schedule_silence.return_value = mock_silence_id
    alertmanager_account = MagicMock()
    result = patch_and_reboot(
        alertmanager_account,
        icinga_account,
        hypervisor_name=mock_hypervisor_name,
        private_key_path=mock_private_key_path,
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
    mock_silence_details_instance = SilenceDetails(
        matchers=AlertMatcherDetails(name="instance", value="test_host"),
        start_time_dt=datetime.datetime.utcnow(),
        duration_hours=6,
        author="stackstorm",
        comment="Stackstorm HV maintenance",
    )
    mock_silence_details_hostname = SilenceDetails(
        matchers=AlertMatcherDetails(name="hostname", value="test_host"),
        start_time_dt=datetime.datetime.utcnow(),
        duration_hours=6,
        author="stackstorm",
        comment="Stackstorm HV maintenance",
    )
    mock_schedule_silence.assert_has_calls(
        [
            call(alertmanager_account, mock_silence_details_instance),
            call(alertmanager_account, mock_silence_details_hostname),
        ]
    )
    mock_ssh_conn.assert_called_once_with(
        SSHDetails(
            host=mock_hypervisor_name,
            username="stackstorm",
            private_key_path=mock_private_key_path,
        )
    )
    mock_ssh_conn.return_value.run_command_on_host.assert_any_call("patch")
    mock_ssh_conn.return_value.run_command_on_host.assert_any_call("reboot")
    assert result["patch_output"] == "Patch command output"
    assert result["reboot_output"] == "Reboot command output"


@patch("workflows.hv_patch_and_reboot.schedule_silence")
@patch("workflows.hv_patch_and_reboot.schedule_downtime")
@patch("workflows.hv_patch_and_reboot.SSHConnection")
@patch("workflows.hv_patch_and_reboot.remove_downtime")
def test_failed_schedule_downtime(
    mock_remove_downtime,
    mock_ssh_conn,
    mock_schedule_downtime,
    mock_schedule_silence,
):
    """
    Test unsuccessful running of patch and reboot workflow - where the schedule
    downtime raises an exception.
    """
    icinga_account = MagicMock()
    mock_private_key_path = "/home/stackstorm/.ssh/id_rsa"
    mock_hypervisor_name = "test_host"
    mock_schedule_downtime.side_effect = Exception
    alertmanager_account = MagicMock()

    with pytest.raises(Exception):
        patch_and_reboot(
            alertmanager_account,
            icinga_account,
            hypervisor_name=mock_hypervisor_name,
            private_key_path=mock_private_key_path,
        )

    # check that the ssh connection is still made
    mock_ssh_conn.assert_called_once_with(
        SSHDetails(
            host=mock_hypervisor_name,
            username="stackstorm",
            private_key_path=mock_private_key_path,
        )
    )
    mock_schedule_silence.assert_not_called()

    mock_ssh_conn.return_value.run_command_on_host.assert_not_called()
    mock_remove_downtime.assert_not_called()


@pytest.mark.freeze_time
@patch("workflows.hv_patch_and_reboot.schedule_silence")
@patch("workflows.hv_patch_and_reboot.remove_silence")
@patch("workflows.hv_patch_and_reboot.remove_downtime")
@patch("workflows.hv_patch_and_reboot.schedule_downtime")
@patch("workflows.hv_patch_and_reboot.SSHConnection")
def test_failed_ssh(
    mock_ssh_conn,
    mock_schedule_downtime,
    mock_remove_downtime,
    mock_remove_silence,
    mock_schedule_silence,
):
    """
    Test unsuccessful running of patch and reboot workflow - where either ssh command
    fails
    """
    icinga_account = MagicMock()
    mock_hypervisor_name = "test_host"
    mock_private_key_path = "/home/stackstorm/.ssh/id_rsa"
    mock_ssh_conn.return_value.run_command_on_host.side_effect = SSHException
    mock_silence_id = "mock_silence_id"
    mock_schedule_silence.return_value = mock_silence_id
    alertmanager_account = MagicMock()

    with pytest.raises(Exception):
        patch_and_reboot(
            alertmanager_account,
            icinga_account,
            hypervisor_name=mock_hypervisor_name,
            private_key_path=mock_private_key_path,
        )

    mock_ssh_conn.assert_called_once_with(
        SSHDetails(
            host=mock_hypervisor_name,
            username="stackstorm",
            private_key_path=mock_private_key_path,
        )
    )
    mock_start_time = datetime.datetime.utcnow()
    mock_end_time = mock_start_time + datetime.timedelta(hours=6)
    mock_start_timestamp = int(mock_start_time.timestamp())
    mock_end_timestamp = int(mock_end_time.timestamp())
    mock_schedule_downtime.assert_called_once_with(
        icinga_account=icinga_account,
        details=DowntimeDetails(
            object_type=IcingaObject.HOST,
            object_name=mock_hypervisor_name,
            start_time=mock_start_timestamp,
            end_time=mock_end_timestamp,
            comment=f"starting downtime to patch and reboot host: {mock_hypervisor_name}",
            is_fixed=True,
            duration=mock_end_timestamp - mock_start_timestamp,
        ),
    )
    mock_silence_details = SilenceDetails(
        matchers=(
            AlertMatcherDetails(name="instance", value="test_host"),
            AlertMatcherDetails(name="hostname", value="test_host"),
        ),
        start_time_dt=datetime.datetime.utcnow(),
        duration_hours=6,
        author="stackstorm",
        comment="Stackstorm HV maintenance",
    )

    mock_schedule_silence.assert_called_once_with(
        alertmanager_account, mock_silence_details
    )

    mock_remove_downtime.assert_called_once_with(
        icinga_account=icinga_account,
        object_type=IcingaObject.HOST,
        object_name=mock_hypervisor_name,
    )
    mock_remove_silence.assert_called_once_with(alertmanager_account, mock_silence_id)
