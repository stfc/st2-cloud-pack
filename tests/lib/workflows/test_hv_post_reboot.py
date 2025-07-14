from unittest.mock import MagicMock, patch, call
import pytest

from apis.icinga_api.enums.icinga_objects import IcingaObject

from workflows.hv_post_reboot import post_reboot


@patch("workflows.hv_post_reboot.remove_silence")
@patch("workflows.hv_post_reboot.get_hv_silences")
@patch("workflows.hv_post_reboot.enable_service")
@patch("workflows.hv_post_reboot.create_test_server")
@patch("workflows.hv_post_reboot.downtime.remove_downtime")
def test_successful_post_reboot(
    mock_remove_downtime,
    mock_create_test_server,
    mock_enable_service,
    mock_get_hv_silences,
    mock_remove_silence,
):
    """
    Test successfull running of the post reboot workflow.
    """
    mock_icinga_account = MagicMock()
    mock_hv_name = "hvxyz"
    mock_conn = MagicMock()
    alertmanager_account = MagicMock()
    mock_silences = {
        "id1": {"state": "active", "details": "details"},
        "id2": {"state": "active", "details": "details"},
    }
    mock_get_hv_silences.return_value = mock_silences

    post_reboot(
        alertmanager_account,
        icinga_account=mock_icinga_account,
        hypervisor_hostname=mock_hv_name,
        conn=mock_conn,
    )
    mock_remove_downtime.assert_called_once_with(
        icinga_account=mock_icinga_account,
        object_type=IcingaObject.HOST,
        object_name=mock_hv_name,
    )
    mock_create_test_server.assert_called_once_with(
        conn=mock_conn,
        hypervisor_name=mock_hv_name,
        test_all_flavors=False,
        delete_on_failure=True,
    )
    mock_enable_service.assert_called_once_with(
        conn=mock_conn, hypervisor_name=mock_hv_name, service_binary="nova-compute"
    )
    mock_get_hv_silences.assert_called_once_with(alertmanager_account, mock_hv_name)
    mock_remove_silence.assert_has_calls(
        [call(alertmanager_account, "id1"), call(alertmanager_account, "id2")],
        any_order=True,
    )


@patch("workflows.hv_post_reboot.remove_silence")
@patch("workflows.hv_post_reboot.get_hv_silences")
@patch("workflows.hv_post_reboot.enable_service")
@patch("workflows.hv_post_reboot.create_test_server")
@patch("workflows.hv_post_reboot.downtime.remove_downtime")
def test_failed_post_reboot(
    mock_remove_downtime,
    mock_create_test_server,
    mock_enable_service,
    mock_get_hv_silences,
    mock_remove_silence,
):
    """
    Test unsuccessful running of the post reboot workflow, where create_test_server fails
    """
    mock_icinga_account = MagicMock()
    mock_hv_name = "hvxyz"
    mock_conn = MagicMock()
    alertmanager_account = MagicMock()
    mock_silences = {
        "id1": {"state": "active", "details": "details"},
        "id2": {"state": "active", "details": "details"},
    }
    mock_get_hv_silences.return_value = mock_silences
    mock_create_test_server.side_effect = Exception

    with pytest.raises(Exception):
        post_reboot(
            alertmanager_account,
            icinga_account=mock_icinga_account,
            hypervisor_hostname=mock_hv_name,
            conn=mock_conn,
        )
    mock_remove_downtime.assert_called_once_with(
        icinga_account=mock_icinga_account,
        object_type=IcingaObject.HOST,
        object_name=mock_hv_name,
    )
    mock_enable_service.assert_called_once_with(
        conn=mock_conn, hypervisor_name=mock_hv_name, service_binary="nova-compute"
    )
    mock_create_test_server.assert_called_once_with(
        conn=mock_conn,
        hypervisor_name=mock_hv_name,
        test_all_flavors=False,
        delete_on_failure=True,
    )
    mock_get_hv_silences.assert_not_called()
    mock_remove_silence.assert_not_called()
