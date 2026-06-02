from unittest.mock import MagicMock, patch
import pytest
from workflows.hv_shutdown_servers import shutdown_all_servers_in_hypervisor


def test_shutdown_all_servers_in_hypervisor_raises_on_empty_hostname():
    """
    Test an Exception is raised when the hostname value passed to function
    shutdown_all_servers_in_hypervisor is empty
    """
    mock_conn = MagicMock()

    with pytest.raises(ValueError):
        shutdown_all_servers_in_hypervisor(mock_conn, "")


def test_shutdown_all_servers_in_hypervisor_raises_on_comma_in_hostname():
    """
    Test an Exception is raised when the hostname value passed to function
    shutdown_all_servers_in_hypervisor includes a comma
    """
    mock_conn = MagicMock()

    with pytest.raises(ValueError):
        shutdown_all_servers_in_hypervisor(mock_conn, "hv1,example.com")


def test_shutdown_all_servers_in_hypervisor_raises_on_colon_in_hostname():
    """
    Test an Exception is raised when the hostname value passed to function
    shutdown_all_servers_in_hypervisor includes a colon
    """
    mock_conn = MagicMock()

    with pytest.raises(ValueError):
        shutdown_all_servers_in_hypervisor(mock_conn, "hv1:example.com")


@patch("workflows.hv_shutdown_servers.find_servers_on_hv")
@patch("workflows.hv_shutdown_servers.shutoff_server_list")
def test_shutoff_server_list_exception_is_reraised(
    mock_shutoff_list, mock_find_servers
):
    mock_conn = MagicMock()

    # Mock the query chain: find_servers_on_hv().to_objects() returns a list with a mock server
    mock_server = MagicMock()
    mock_server.id = "server-123"
    mock_find_servers.return_value.to_objects.return_value = [mock_server]

    # Set the expected exception on the shutdown function
    expected_exception = Exception("test error")
    mock_shutoff_list.side_effect = expected_exception

    with pytest.raises(Exception) as exc:
        shutdown_all_servers_in_hypervisor(mock_conn, "hv1.example.com")

    assert exc.value is expected_exception
