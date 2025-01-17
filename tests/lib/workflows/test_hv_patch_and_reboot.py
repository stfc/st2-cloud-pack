import datetime
from unittest.mock import MagicMock, patch

from paramiko import SSHException
from enums.icinga.icinga_objects import IcingaObject
from structs.icinga.downtime_details import DowntimeDetails
from structs.ssh.ssh_connection_details import SSHDetails
from workflows.hv_patch_and_reboot import patch_and_reboot
import pytest


@patch("workflows.hv_patch_and_reboot.schedule_downtime")
@patch("workflows.hv_patch_and_reboot.SSHConnection")
def test_successful_patch_and_reboot(
    mock_ssh_conn,
    mock_schedule_downtime,
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
    result = patch_and_reboot(
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


@patch("workflows.hv_patch_and_reboot.schedule_downtime")
@patch("workflows.hv_patch_and_reboot.SSHConnection")
@patch("workflows.hv_patch_and_reboot.remove_downtime")
def test_failed_schedule_downtime(
    mock_remove_downtime, mock_ssh_conn, mock_schedule_downtime
):
    """
    Test unsuccessful running of patch and reboot workflow - where the schedule
    downtime raises an exception.
    """
    icinga_account = MagicMock()
    mock_private_key_path = "/home/stackstorm/.ssh/id_rsa"
    mock_hypervisor_name = "test_host"
    mock_schedule_downtime.side_effect = Exception

    with pytest.raises(Exception):
        patch_and_reboot(
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

    mock_ssh_conn.return_value.run_command_on_host.assert_not_called()
    mock_remove_downtime.assert_not_called()


@patch("workflows.hv_patch_and_reboot.remove_downtime")
@patch("workflows.hv_patch_and_reboot.schedule_downtime")
@patch("workflows.hv_patch_and_reboot.SSHConnection")
def test_failed_ssh(mock_ssh_conn, mock_schedule_downtime, mock_remove_downtime):
    """
    Test unsuccessful running of patch and reboot workflow - where either ssh command
    fails
    """
    icinga_account = MagicMock()
    mock_hypervisor_name = "test_host"
    mock_private_key_path = "/home/stackstorm/.ssh/id_rsa"
    mock_ssh_conn.return_value.run_command_on_host.side_effect = SSHException

    with pytest.raises(Exception):
        patch_and_reboot(
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
    mock_remove_downtime.assert_called_once_with(
        icinga_account=icinga_account,
        object_type=IcingaObject.HOST,
        object_name=mock_hypervisor_name,
    )
