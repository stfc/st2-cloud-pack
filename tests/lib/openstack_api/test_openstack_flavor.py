from unittest.mock import MagicMock, patch
import pytest
from openstack_api.openstack_flavor import OpenstackFlavor


@pytest.fixture(name="sensor")
def flavor_api_fixture():
    """
    Fixture for sensor config.
    """
    return OpenstackFlavor()


@patch("openstack_api.openstack_flavor.OpenstackConnection")
def test_list_flavors(mock_openstack_connection):
    """
    Test getting list of flavors
    """
    mock_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.return_value = mock_conn

    mock_list = MagicMock()
    mock_conn.list_flavors.return_value = [mock_list]

    mock_conn.list_flavors.assert_called()
