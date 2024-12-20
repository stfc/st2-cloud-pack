from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest
from openstack_api.openstack_server import snapshot_and_migrate_server, snapshot_server


@pytest.mark.parametrize("dest_host", [None, "hv01"])
@patch("openstack_api.openstack_server.snapshot_server")
def test_active_migration(mock_snapshot_server, dest_host):
    """
    Test migration when the status of the server is ACTIVE and the destination host is supplied
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server_status = "ACTIVE"
    snapshot_and_migrate_server(
        conn=mock_connection,
        server_id=mock_server_id,
        server_status=mock_server_status,
        dest_host=dest_host,
    )
    mock_snapshot_server.assert_called_once_with(
        conn=mock_connection, server_id=mock_server_id
    )
    mock_connection.compute.live_migrate_server.assert_called_once_with(
        server=mock_server_id, host=dest_host, block_migration=True
    )
    mock_connection.compute.migrate_server.assert_not_called()


@pytest.mark.parametrize("dest_host", [None, "hv01"])
@patch("openstack_api.openstack_server.snapshot_server")
def test_shutoff_migration(mock_snapshot_server, dest_host):
    """
    Test migration when the status of the server is SHUTOFF and the destination host is supplied
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server_status = "SHUTOFF"
    snapshot_and_migrate_server(
        conn=mock_connection,
        server_id=mock_server_id,
        server_status=mock_server_status,
        dest_host=dest_host,
    )
    mock_snapshot_server.assert_called_once_with(
        conn=mock_connection, server_id=mock_server_id
    )
    mock_connection.compute.live_migrate_server.assert_not_called()
    mock_connection.compute.migrate_server.assert_called_once_with(
        server=mock_server_id, host=dest_host
    )


@patch("openstack_api.openstack_server.snapshot_server")
def test_migration_fail(mock_snapshot_server):
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server_status = "TEST"
    with pytest.raises(
        ValueError,
        match="Server status: TEST. The server must be ACTIVE or SHUTOFF to be migrated",
    ):
        snapshot_and_migrate_server(
            conn=mock_connection,
            server_id=mock_server_id,
            server_status=mock_server_status,
        )
    mock_snapshot_server.assert_called_once_with(
        conn=mock_connection, server_id=mock_server_id
    )
    mock_connection.compute.live_migrate_server.assert_not_called()
    mock_connection.compute.migrate_server.assert_not_called()


def test_snapshot_server():
    """
    Test server snapshot
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    current_time = datetime.now().strftime("%d-%m-%Y-%H%M")

    mock_project_id = "project1"
    mock_connection.compute.find_server.return_value.project_id = mock_project_id

    mock_image = MagicMock()
    mock_connection.compute.create_server_image.return_value = mock_image

    snapshot_server(conn=mock_connection, server_id=mock_server_id)

    mock_connection.compute.find_server.assert_called_once_with(
        mock_server_id, all_projects=True
    )
    mock_connection.compute.create_server_image.assert_called_once_with(
        server=mock_server_id,
        name=f"{mock_server_id}-{current_time}",
        wait=True,
        timeout=300,
    )
    mock_connection.image.update_image.assert_called_once_with(
        mock_image, owner=mock_project_id
    )
