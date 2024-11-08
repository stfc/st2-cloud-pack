from unittest.mock import MagicMock, patch
from workflows.hv_patch_and_reboot import patch_and_reboot


@patch("workflows.hv_patch_and_reboot.schedule_downtime")
@patch("workflows.hv_patch_and_reboot.ssh_remote_command")
@patch("workflows.hv_patch_and_reboot.remove_downtime")
def test_successful_patch_and_reboot(
    mock_remove_downtime, mock_ssh_remote_command, mock_schedule_downtime
):
    """
    Test successful running of patch and reboot workflow
    """
    icinga_account = MagicMock()
    # patch for first run and reboot for second call of the mock function
    mock_ssh_remote_command.side_effect = [
        "Patch command output",
        "Reboot command output",
    ]
    name = "example_host"
    comment = f"starting downtime to patch and reboot host: {name}"
    mock_host = "test_host"
    mock_private_key_path = "/home/stackstorm/.ssh/id_rsa"

    result = patch_and_reboot(
        icinga_account,
        "example_host",
        "01/12/24 12:00:00",
        "01/12/24 17:00:00",
        host=mock_host,
        private_key_path=mock_private_key_path,
    )
    # test that schedule downtime is called once with expected parameters
    mock_schedule_downtime.assert_called_once_with(
        icinga_account=icinga_account,
        object_type="Host",
        name=name,
        start_time="01/12/24 12:00:00",
        end_time="01/12/24 17:00:00",
        is_fixed=True,
        comment=comment,
    )
    # test that the two ssh remote commands are run and that their results are as expected
    mock_ssh_remote_command.assert_any_call(
        host=mock_host,
        username="stackstorm",
        private_key_path=mock_private_key_path,
        command=f"{mock_host} patch",
    )
    mock_ssh_remote_command.assert_any_call(
        host=mock_host,
        username="stackstorm",
        private_key_path=mock_private_key_path,
        command=f"{mock_host} reboot",
    )
    assert result["patch_output"] == "Patch command output"
    assert result["reboot_output"] == "Reboot command output"

    # test that the remove downtime is called
    mock_remove_downtime.assert_called_once_with(
        icinga_account=icinga_account, object_type="Host", name=name
    )


"""
Need to test:
+ What happens when the schedule downtime doesnt work
+ What happens when one of the ssh requests doesnt work
"""
