from unittest.mock import MagicMock, patch, call

from enums.icinga.icinga_objects import IcingaObject

from workflows.hv_post_reboot import post_reboot


@patch("workflows.hv_post_reboot.remove_silence")
@patch("workflows.hv_post_reboot.get_hv_silences")
@patch("workflows.hv_post_reboot.hv_service_enable")
@patch("workflows.hv_post_reboot.create_test_server")
@patch("workflows.hv_post_reboot.downtime.remove_downtime")
def test_successful_post_reboot(
    mock_remove_downtime,
    mock_create_test_server,
    mock_hv_service_enable,
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
        name=mock_hv_name,
        conn=mock_conn,
    )
    mock_remove_downtime.assert_called_once_with(
        icinga_account=mock_icinga_account,
        object_type=IcingaObject.HOST,
        object_name=mock_hv_name,
    )

    mock_get_hv_silences.assert_called_once_with(alertmanager_account, mock_hv_name)
    mock_remove_silence.assert_has_calls(
        [call(alertmanager_account, "id1"), call(alertmanager_account, "id2")],
        any_order=True,
    )
    mock_create_test_server.assert_called_once_with(
        conn=mock_conn, hypervisor_name=mock_hv_name, test_all_flavors=False
    )
    mock_hv_service_enable.assert_called_once_with(
        conn=mock_conn, hypervisor_name=mock_hv_name, service_binary="nova-compute"
    )
