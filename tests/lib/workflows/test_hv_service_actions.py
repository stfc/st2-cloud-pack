from unittest.mock import MagicMock, patch, NonCallableMagicMock
from workflows.hv_service_actions import hv_service_disable, hv_service_enable


@patch("workflows.hv_service_actions.disable_service")
def test_service_disabled_successfully(mock_hv_service_disable):
    """test that hv_service_disable disables an openstack service"""

    mock_conn = MagicMock()
    mock_hypervisor_name = NonCallableMagicMock()
    mock_service_binary = NonCallableMagicMock()
    mock_disabled_reason = NonCallableMagicMock()

    hv_service_disable(
        mock_conn, mock_hypervisor_name, mock_service_binary, mock_disabled_reason
    )

    mock_conn.compute.find_service.assert_called_once_with(
        mock_service_binary, ignore_missing=False, host=mock_hypervisor_name
    )

    mock_hv_service_disable.assert_called_once_with(
        mock_conn,
        mock_conn.compute.find_service.return_value,
        mock_hypervisor_name,
        mock_service_binary,
        mock_disabled_reason,
    )


@patch("workflows.hv_service_actions.enable_service")
def test_hv_service_enabled_successfully(mock_hv_service_enable):
    """test that hv_service_enable enables an openstack service"""

    mock_conn = MagicMock()
    mock_hypervisor_name = NonCallableMagicMock()
    mock_service_binary = NonCallableMagicMock()

    hv_service_enable(mock_conn, mock_hypervisor_name, mock_service_binary)

    mock_conn.compute.find_service.assert_called_once_with(
        mock_service_binary, ignore_missing=False, host=mock_hypervisor_name
    )

    mock_hv_service_enable.assert_called_once_with(
        mock_conn,
        mock_conn.compute.find_service.return_value,
        mock_hypervisor_name,
        mock_service_binary,
    )
