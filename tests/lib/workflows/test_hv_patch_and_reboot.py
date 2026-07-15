import datetime
from unittest.mock import MagicMock, patch, call
from paramiko import SSHException

from apis.alertmanager_api.structs.alert_matcher_details import AlertMatcherDetails
from apis.alertmanager_api.structs.silence_details import SilenceDetails
from apis.ssh_api.structs.ssh_connection_details import SSHDetails
from workflows.hv_patch_and_reboot import patch_and_reboot
import pytest


# pylint:disable=too-many-locals
@pytest.mark.freeze_time
@patch("workflows.hv_patch_and_reboot.schedule_silence")
@patch("workflows.hv_patch_and_reboot.SSHConnection")
def test_successful_patch_and_reboot(
    mock_ssh_conn,
    mock_schedule_silence,
):
    """
    Test successful running of patch and reboot workflow
    """
    mock_hypervisor_name = "test_host"
    mock_private_key_path = "/home/stackstorm/.ssh/id_rsa"
    mock_silence_id = "mock ID"
    mock_schedule_silence.return_value = mock_silence_id
    alertmanager_account = MagicMock()
    patch_and_reboot(
        alertmanager_account,
        hypervisor_name=mock_hypervisor_name,
        private_key_path=mock_private_key_path,
    )
    mock_silence_details_instance = SilenceDetails(
        matchers=[AlertMatcherDetails(name="instance", value="test_host")],
        start_time_dt=datetime.datetime.utcnow(),
        duration_hours=6,
        author="stackstorm",
        comment="Stackstorm: HV Patching",
    )
    mock_silence_details_hostname = SilenceDetails(
        matchers=[AlertMatcherDetails(name="hostname", value="test_host")],
        start_time_dt=datetime.datetime.utcnow(),
        duration_hours=6,
        author="stackstorm",
        comment="Stackstorm: HV Patching",
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


@pytest.mark.freeze_time
@patch("workflows.hv_patch_and_reboot.schedule_silence")
@patch("workflows.hv_patch_and_reboot.remove_silence")
@patch("workflows.hv_patch_and_reboot.SSHConnection")
def test_failed_ssh(
    mock_ssh_conn,
    mock_remove_silence,
    mock_schedule_silence,
):
    """
    Test unsuccessful running of patch and reboot workflow - where either ssh command
    fails
    """
    mock_hypervisor_name = "test_host"
    mock_private_key_path = "/home/stackstorm/.ssh/id_rsa"
    mock_ssh_conn.return_value.run_command_on_host.side_effect = SSHException
    mock_silence_id = "mock_silence_id"
    mock_schedule_silence.return_value = mock_silence_id
    alertmanager_account = MagicMock()

    with pytest.raises(Exception):
        patch_and_reboot(
            alertmanager_account,
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
    mock_silence_details_instance = SilenceDetails(
        matchers=[AlertMatcherDetails(name="instance", value="test_host")],
        start_time_dt=datetime.datetime.utcnow(),
        duration_hours=6,
        author="stackstorm",
        comment="Stackstorm: HV Patching",
    )
    mock_silence_details_hostname = SilenceDetails(
        matchers=[AlertMatcherDetails(name="hostname", value="test_host")],
        start_time_dt=datetime.datetime.utcnow(),
        duration_hours=6,
        author="stackstorm",
        comment="Stackstorm: HV Patching",
    )
    mock_schedule_silence.assert_has_calls(
        [
            call(alertmanager_account, mock_silence_details_instance),
            call(alertmanager_account, mock_silence_details_hostname),
        ]
    )

    mock_remove_silence.assert_has_calls(
        [
            call(alertmanager_account, mock_silence_id),
            call(alertmanager_account, mock_silence_id),
        ]
    )
