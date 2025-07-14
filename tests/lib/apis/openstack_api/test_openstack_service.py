from unittest.mock import MagicMock, NonCallableMagicMock
from apis.openstack_api.openstack_service import enable_service, disable_service


def test_service_disabled_successfully():
    """test that hv_service_disable disables an openstack service"""

    mock_conn = MagicMock()
    mock_hypervisor_name = NonCallableMagicMock()
    mock_service_binary = NonCallableMagicMock()
    mock_disabled_reason = NonCallableMagicMock()

    mock_service = MagicMock()
    mock_conn.compute.find_service.return_value = mock_service

    disable_service(
        mock_conn,
        mock_hypervisor_name,
        mock_service_binary,
        mock_disabled_reason,
    )

    mock_conn.compute.find_service.assert_called_once_with(
        mock_service_binary, ignore_missing=False, host=mock_hypervisor_name
    )

    mock_conn.compute.disable_service.assert_called_once_with(
        service=mock_service.id,
        disabled_reason=mock_disabled_reason,
    )


def test_hv_service_enabled_successfully():
    """test that hv_service_enable enables an openstack service"""

    mock_conn = MagicMock()
    mock_hypervisor_name = NonCallableMagicMock()
    mock_service_binary = NonCallableMagicMock()

    mock_service = MagicMock()
    mock_conn.compute.find_service.return_value = mock_service

    enable_service(mock_conn, mock_hypervisor_name, mock_service_binary)

    mock_conn.compute.find_service.assert_called_once_with(
        mock_service_binary, ignore_missing=False, host=mock_hypervisor_name
    )

    mock_conn.compute.enable_service.assert_called_once_with(
        service=mock_service.id,
    )
