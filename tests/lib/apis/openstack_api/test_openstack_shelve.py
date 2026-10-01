from unittest.mock import MagicMock, NonCallableMock, patch, ANY

import pytest
from openstack.exceptions import (
    ResourceNotFound,
)

from apis.openstack_api.openstack_server import (
    shelve_server,
    get_server_metadata,
)


def _mock_connection(status: str) -> MagicMock:
    conn = MagicMock()
    mock_server = MagicMock()
    mock_server.id = "server1"
    mock_server.name = "vm1"
    mock_server.status = status
    conn.compute.find_server.return_value = mock_server
    return conn


def _mock_server(server_id: str = "server1") -> MagicMock:
    server = MagicMock()
    server.id = server_id
    return server


def test_shelve_server_raises_when_server_does_not_exist():
    """
    Tests that a missing server raises ResourceNotFound
    instead of AttributeError if a server isn't found
    """
    conn = _mock_connection("SHUTOFF")
    conn.compute.find_server.side_effect = ResourceNotFound("no such server")
    all_projects = NonCallableMock()

    with pytest.raises(ResourceNotFound):
        shelve_server(conn, "server1", all_projects=all_projects)

    conn.compute.find_server.assert_called_once_with(
        "server1", ignore_missing=False, all_projects=all_projects
    )
    conn.compute.shelve_server.assert_not_called()


def test_shelve_server_shelves_shutoff_server():
    """
    Tests that a SHUTOFF server is shelved and we wait for
    a SHELVED or SHELVED_OFFLOADED state before returning
    """
    conn = _mock_connection("SHUTOFF")
    conn.compute.get_server.return_value.status = "SHELVED"
    all_projects = NonCallableMock()

    shelve_server(conn, "server1", all_projects=all_projects)

    conn.compute.find_server.assert_called_once_with(
        "server1", ignore_missing=False, all_projects=all_projects
    )
    conn.compute.shelve_server.assert_called_once_with(
        conn.compute.find_server.return_value
    )

    returned = conn.compute.find_server.return_value
    conn.compute.wait_for_server.assert_called_with(
        returned, status="SHELVED", wait=ANY
    )
    conn.compute.set_server_metadata.assert_not_called()


def test_shelve_server_waits_for_shelved_offloaded():
    """
    Tests that SHELVED_OFFLOADED is treated as a valid shelved state
    """
    conn = _mock_connection("SHUTOFF")
    conn.compute.get_server.return_value.status = "SHELVED_OFFLOADED"

    with patch("apis.openstack_api.openstack_server.time.sleep"):
        shelve_server(conn, "server1")

    conn.compute.shelve_server.assert_called_once()
    conn.compute.set_server_metadata.assert_not_called()


def test_shelve_server_skips_shelving_already_sheled_server():
    """
    Tests that a SHELVED server is skipped
    """
    conn = _mock_connection("SHELVED")

    shelve_server(conn, "server1")

    conn.compute.shelve_server.assert_not_called()
    conn.compute.get_server.assert_not_called()
    conn.compute.set_server_metadata.assert_not_called()


def test_shelve_server_skips_shelving_already_offloaded_server():
    """
    Tests a SHELVED_OFFLOADED server is skipped
    """
    conn = _mock_connection("SHELVED_OFFLOADED")

    shelve_server(conn, "server1")

    conn.compute.shelve_server.assert_not_called()
    conn.compute.get_server.assert_not_called()
    conn.compute.set_server_metadata.assert_not_called()


def test_shelve_server_raises_when_server_not_shutoff():
    """
    Tests that a server which is not SHUTOFF or already shelved raises ValueError
    """
    conn = _mock_connection("ACTIVE")

    with pytest.raises(ValueError, match="must be SHUTOFF"):
        shelve_server(conn, "server1")

    conn.compute.shelve_server.assert_not_called()
    conn.compute.set_server_metadata.assert_not_called()


def test_get_server_metadata():
    """
    Tests the get_server_metadata returns the metadata of a server as a dictionary of key:values
    """
    conn = MagicMock()
    conn.compute.find_server.return_value.metadata = {"key": "value"}
    all_projects = NonCallableMock()

    metadata = get_server_metadata(conn, "server1", all_projects=all_projects)

    conn.compute.find_server.assert_called_once_with(
        "server1", ignore_missing=False, all_projects=all_projects
    )
    assert metadata == {"key": "value"}


def test_get_server_metadata_returns_empty_dict_when_metadata_is_none():
    """
    Tests that get_server_metadata returns an empty dictionary when the server metadata is None
    """
    conn = MagicMock()
    conn.compute.find_server.return_value.metadata = None

    assert get_server_metadata(conn, "server1") == {}
