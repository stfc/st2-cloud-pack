from datetime import datetime
from unittest.mock import MagicMock, patch
from openstack.exceptions import ResourceFailure
import pytest
from openstack_api.openstack_server import (
    build_server,
    delete_server,
    snapshot_and_migrate_server,
    snapshot_server,
)


@pytest.mark.parametrize("dest_host", [None, "hv01"])
@patch("openstack_api.openstack_server.snapshot_server")
def test_active_migration(mock_snapshot_server, dest_host):
    """
    Test migration when the status of the server is ACTIVE and the destination host is supplied
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server_status = "ACTIVE"
    mock_flavor_id = "mock_flavor"
    snapshot_and_migrate_server(
        conn=mock_connection,
        server_id=mock_server_id,
        server_status=mock_server_status,
        flavor_id=mock_flavor_id,
        dest_host=dest_host,
        snapshot=True,
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
    mock_flavor_id = "mock_flavor"
    snapshot_and_migrate_server(
        conn=mock_connection,
        server_id=mock_server_id,
        server_status=mock_server_status,
        flavor_id=mock_flavor_id,
        dest_host=dest_host,
        snapshot=True,
    )
    mock_snapshot_server.assert_called_once_with(
        conn=mock_connection, server_id=mock_server_id
    )
    mock_connection.compute.live_migrate_server.assert_not_called()
    mock_connection.compute.migrate_server.assert_called_once_with(
        server=mock_server_id, host=dest_host
    )


@patch("openstack_api.openstack_server.snapshot_server")
def test_no_snapshot_migration(mock_snapshot_server):
    """
    Test migration with no snapshot
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server_status = "ACTIVE"
    mock_flavor_id = "mock_flavor"
    snapshot_and_migrate_server(
        conn=mock_connection,
        server_id=mock_server_id,
        server_status=mock_server_status,
        flavor_id=mock_flavor_id,
        snapshot=False,
    )
    mock_snapshot_server.assert_not_called()


@patch("openstack_api.openstack_server.snapshot_server")
def test_migration_fail(mock_snapshot_server):
    """
    Test failure of migration when the status is not ACTIVE or SHUTOFF
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server_status = "TEST"
    mock_flavor_id = "mock_flavor"
    with pytest.raises(
        ValueError,
        match="Server status: TEST. The server must be ACTIVE or SHUTOFF to be migrated",
    ):
        snapshot_and_migrate_server(
            conn=mock_connection,
            server_id=mock_server_id,
            server_status=mock_server_status,
            flavor_id=mock_flavor_id,
            snapshot=True,
        )
    mock_snapshot_server.assert_not_called()
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
        timeout=3600,
    )
    mock_connection.image.update_image.assert_called_once_with(
        mock_image, owner=mock_project_id
    )


def test_block_gpu_migration():
    """
    Test migration of gpu flavor raises error
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server_status = "SHUTOFF"
    mock_flavor_id = "g-a100-80gb-2022.x2"

    with pytest.raises(ValueError):
        snapshot_and_migrate_server(
            conn=mock_connection,
            server_id=mock_server_id,
            server_status=mock_server_status,
            flavor_id=mock_flavor_id,
            dest_host=None,
            snapshot=True,
        )


def test_build_server():
    """
    Test build server on a given hypervisor
    """
    mock_conn = MagicMock()

    mock_conn.compute.find_flavor.return_value = MagicMock()
    mock_conn.image.find_image.return_value = MagicMock()
    mock_conn.network.find_network.return_value = MagicMock()

    mock_server = MagicMock()
    mock_conn.compute.create_server.return_value = mock_server

    res = build_server(
        mock_conn,
        "test-server",
        "test-flavor",
        "test-image",
        "test-network",
        "hvxyz.nubes.rl.ac.uk",
        False,
    )

    mock_conn.compute.find_flavor.assert_called_once_with("test-flavor")
    mock_conn.image.find_image.assert_called_once_with("test-image")
    mock_conn.network.find_network.assert_called_once_with("test-network")

    mock_conn.compute.create_server.assert_called_once_with(
        **{
            "name": "test-server",
            "imageRef": mock_conn.image.find_image.return_value.id,
            "flavorRef": mock_conn.compute.find_flavor.return_value.id,
            "networks": [{"uuid": mock_conn.network.find_network.return_value.id}],
            "host": "hvxyz.nubes.rl.ac.uk",
            "openstack_api_version": "2.74",
        }
    )
    mock_conn.compute.wait_for_server.assert_called_once_with(
        mock_server, status="ACTIVE", failures=None, interval=5, wait=300
    )

    assert res == mock_server


def test_build_server_delete_on_failure():
    """
    Test build server with delete on failure set to True
    """
    mock_conn = MagicMock()

    mock_conn.compute.find_flavor.return_value = MagicMock()
    mock_conn.image.find_image.return_value = MagicMock()
    mock_conn.network.find_network.return_value = MagicMock()

    mock_server = MagicMock()
    mock_conn.compute.create_server.return_value = mock_server

    mock_conn.compute.wait_for_server.side_effect = ResourceFailure("Failure")

    with pytest.raises(ResourceFailure):
        build_server(
            mock_conn,
            "test-server",
            "test-flavor",
            "test-image",
            "test-network",
            "hvxyz.nubes.rl.ac.uk",
            delete_on_failure=True,
        )

    mock_conn.compute.find_flavor.assert_called_once_with("test-flavor")
    mock_conn.image.find_image.assert_called_once_with("test-image")
    mock_conn.network.find_network.assert_called_once_with("test-network")

    mock_conn.compute.create_server.assert_called_once_with(
        **{
            "name": "test-server",
            "imageRef": mock_conn.image.find_image.return_value.id,
            "flavorRef": mock_conn.compute.find_flavor.return_value.id,
            "networks": [{"uuid": mock_conn.network.find_network.return_value.id}],
            "host": "hvxyz.nubes.rl.ac.uk",
            "openstack_api_version": "2.74",
        }
    )
    mock_conn.compute.wait_for_server.assert_called_once_with(
        mock_server, status="ACTIVE", failures=None, interval=5, wait=300
    )
    mock_conn.compute.delete_server.assert_called_once_with(mock_server, force=True)


def test_build_server_delete_on_failure_false():
    """
    Test build server with delete on failure set to False
    """
    mock_conn = MagicMock()

    mock_conn.compute.find_flavor.return_value = MagicMock()
    mock_conn.image.find_image.return_value = MagicMock()
    mock_conn.network.find_network.return_value = MagicMock()

    mock_server = MagicMock()
    mock_conn.compute.create_server.return_value = mock_server

    mock_conn.compute.wait_for_server.side_effect = ResourceFailure("Failure")

    with pytest.raises(ResourceFailure):
        build_server(
            mock_conn,
            "test-server",
            "test-flavor",
            "test-image",
            "test-network",
            "hvxyz.nubes.rl.ac.uk",
            delete_on_failure=False,
        )

    mock_conn.compute.find_flavor.assert_called_once_with("test-flavor")
    mock_conn.image.find_image.assert_called_once_with("test-image")
    mock_conn.network.find_network.assert_called_once_with("test-network")

    mock_conn.compute.create_server.assert_called_once_with(
        **{
            "name": "test-server",
            "imageRef": mock_conn.image.find_image.return_value.id,
            "flavorRef": mock_conn.compute.find_flavor.return_value.id,
            "networks": [{"uuid": mock_conn.network.find_network.return_value.id}],
            "host": "hvxyz.nubes.rl.ac.uk",
            "openstack_api_version": "2.74",
        }
    )
    mock_conn.compute.wait_for_server.assert_called_once_with(
        mock_server, status="ACTIVE", failures=None, interval=5, wait=300
    )
    mock_conn.compute.delete_server.assert_not_called()


def test_delete_server():
    """
    Test deleting server
    """
    mock_conn = MagicMock()

    mock_server = MagicMock()

    mock_conn.compute.find_server.return_value = mock_server

    delete_server(mock_conn, "test-server-id", force=False)

    mock_conn.compute.find_server.assert_called_once_with("test-server-id")
    mock_conn.compute.delete_server.assert_called_once_with(mock_server, False)
    mock_conn.compute.wait_for_delete.assert_called_once_with(
        mock_server, interval=5, wait=300
    )


def test_force_delete_server():
    """
    Test force deleting a server
    """
    mock_conn = MagicMock()

    mock_server = MagicMock()

    mock_conn.compute.find_server.return_value = mock_server

    delete_server(mock_conn, "test-server-id", force=True)

    mock_conn.compute.find_server.assert_called_once_with("test-server-id")
    mock_conn.compute.delete_server.assert_called_once_with(mock_server, True)
    mock_conn.compute.wait_for_delete.assert_called_once_with(
        mock_server, interval=5, wait=300
    )
