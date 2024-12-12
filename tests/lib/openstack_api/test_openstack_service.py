from unittest.mock import MagicMock, NonCallableMagicMock
import pytest
from openstack_api.openstack_service import disable_service, enable_service


def test_disable_service_function_disables_service_when_enabled():
    """tests that openstack disables the service when it is currently enabled"""

    mock_conn = MagicMock()
    mock_service = MagicMock()
    mock_hypervisor_name = NonCallableMagicMock()
    mock_service_binary = NonCallableMagicMock()
    mock_disable_reason = NonCallableMagicMock()

    mock_service.status = "enabled"

    res = disable_service(
        mock_conn,
        mock_service,
        mock_hypervisor_name,
        mock_service_binary,
        mock_disable_reason,
    )

    mock_conn.compute.disable_service.assert_called_once_with(
        mock_service,
        host=mock_hypervisor_name,
        binary=mock_service_binary,
        disabled_reason=mock_disable_reason,
    )

    assert res == mock_conn.compute.disable_service.return_value


def test_disable_service_function_returns_none_when_disabled():
    """tests that openstack returns None when the service is currently disabled"""

    mock_conn = MagicMock()
    mock_service = MagicMock()
    mock_hypervisor_name = NonCallableMagicMock()
    mock_service_binary = NonCallableMagicMock()
    mock_disable_reason = NonCallableMagicMock()

    mock_service.status = "disabled"

    with pytest.raises(RuntimeError):
        disable_service(
            mock_conn,
            mock_service,
            mock_hypervisor_name,
            mock_service_binary,
            mock_disable_reason,
        )


def test_enable_service_function_enables_service_when_disabled():
    """tests that openstack enables the service when it is currently disabled"""

    mock_conn = MagicMock()
    mock_service = MagicMock()
    mock_hypervisor_name = NonCallableMagicMock()
    mock_service_binary = NonCallableMagicMock()

    mock_service.status = "disabled"

    res = enable_service(
        mock_conn, mock_service, mock_hypervisor_name, mock_service_binary
    )

    mock_conn.compute.enable_service.assert_called_once_with(
        mock_service,
        host=mock_hypervisor_name,
        binary=mock_service_binary,
    )

    assert res == mock_conn.compute.enable_service.return_value


def test_enable_service_function_returns_none_when_enabled():
    """tests that openstack returns none when the service is currently enabled"""

    mock_conn = MagicMock()
    mock_service = MagicMock()
    mock_hypervisor_name = NonCallableMagicMock()
    mock_service_binary = NonCallableMagicMock()

    mock_service.status = "enabled"

    with pytest.raises(RuntimeError):
        enable_service(
            mock_conn, mock_service, mock_hypervisor_name, mock_service_binary
        )
