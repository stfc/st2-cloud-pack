from unittest.mock import MagicMock
import pytest


@pytest.fixture(scope="function", name="mock_connection")
def mock_connection_fixture():
    """
    Returns a mocked OpenstackConnection class
    """
    return MagicMock()


@pytest.fixture(scope="function", name="mock_openstack_connection")
def mock_openstack_connection_fixture(mock_connection):
    """
    Returns a mocked openstacksdk connection object
    """
    return mock_connection.return_value.__enter__.return_value
