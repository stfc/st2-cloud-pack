from datetime import datetime
import itertools
from unittest.mock import MagicMock, patch
from openstack.exceptions import ResourceTimeout, ResourceFailure
import pytest
from openstack_api.openstack_server import (
    build_server,
    delete_server,
    snapshot_and_migrate_server,
    snapshot_server,
    wait_for_migration_status,
    wait_for_image_status,
)


@pytest.mark.parametrize("dest_host", [None, "hv01"])
@patch("openstack_api.openstack_server.snapshot_server")
@patch("openstack_api.openstack_server.wait_for_migration_status")
def test_active_migration(
    mock_wait_for_migration_status, mock_snapshot_server, dest_host
):
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
    mock_wait_for_migration_status.assert_called_once_with(
        mock_connection, mock_server_id, "completed"
    )
    mock_connection.compute.migrate_server.assert_not_called()


@pytest.mark.parametrize("dest_host", [None, "hv01"])
@patch("openstack_api.openstack_server.snapshot_server")
@patch("openstack_api.openstack_server.wait_for_migration_status")
def test_shutoff_migration(
    mock_wait_for_migration_status, mock_snapshot_server, dest_host
):
    """
    Test migration when the status of the server is SHUTOFF and the destination host is supplied
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server_status = "SHUTOFF"
    mock_flavor_id = "mock_flavor"
    mock_server = MagicMock()
    mock_connection.compute.get_server.return_value = mock_server
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
    mock_connection.compute.wait_for_server.assert_called_once_with(
        mock_server, status="VERIFY_RESIZE"
    )
    mock_connection.compute.confirm_server_resize(mock_server_id)
    mock_wait_for_migration_status.assert_called_once_with(
        mock_connection, mock_server_id, "confirmed"
    )


@patch("openstack_api.openstack_server.snapshot_server")
@patch("openstack_api.openstack_server.wait_for_migration_status")
def test_active_migration_failed_wait_for_status(
    mock_wait_for_migration_status, mock_snapshot_server
):
    """
    Test migration when the the status of migration raises an error
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server_status = "ACTIVE"
    mock_flavor_id = "mock_flavor"
    mock_wait_for_migration_status.side_effect = ResourceTimeout
    with pytest.raises(ResourceTimeout):
        snapshot_and_migrate_server(
            conn=mock_connection,
            server_id=mock_server_id,
            server_status=mock_server_status,
            flavor_id=mock_flavor_id,
            dest_host=None,
            snapshot=True,
        )
    mock_snapshot_server.assert_called_once_with(
        conn=mock_connection, server_id=mock_server_id
    )
    mock_connection.compute.live_migrate_server.assert_called_once_with(
        server=mock_server_id, host=None, block_migration=True
    )
    mock_wait_for_migration_status.assert_called_once_with(
        mock_connection, mock_server_id, "completed"
    )
    mock_connection.compute.migrate_server.assert_not_called()


@patch("openstack_api.openstack_server.snapshot_server")
@patch("openstack_api.openstack_server.wait_for_migration_status")
def test_no_snapshot_migration(mock_wait_for_migration_status, mock_snapshot_server):
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
    mock_connection.compute.live_migrate_server.assert_called_once_with(
        server=mock_server_id, host=None, block_migration=True
    )
    mock_wait_for_migration_status.assert_called_once_with(
        mock_connection, mock_server_id, "completed"
    )


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


@patch("openstack_api.openstack_server.wait_for_image_status")
def test_snapshot_server(mock_wait_for_image_status):
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
        name=f"st2-{mock_server_id}-{current_time}",
        wait=True,
        timeout=3600,
    )
    mock_wait_for_image_status.assert_called_once_with(
        mock_connection, mock_image, "active"
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


def test_wait_for_image_status_success():
    """
    Test wait_for_image_status when it is a success
    """
    mock_conn = MagicMock()
    image = MagicMock(id="123", name="test-image", status="pending")
    image_final = MagicMock(id="123", name="test-image", status="active")

    mock_conn.image.get_image.side_effect = [
        MagicMock(id="123", name="test-image", status="pending"),
        MagicMock(id="123", name="test-image", status="pending"),
        image_final,
    ]
    result = wait_for_image_status(mock_conn, image, "active", interval=0, timeout=10)
    mock_conn.image.get_image.assert_called_with(image.id)
    assert result == image_final


def test_wait_for_image_status_timeout():
    """
    Test wait_for_image_status when it hits the timeout
    """
    mock_conn = MagicMock()
    image = MagicMock(id="123", name="test-image", status="pending")
    mock_conn.image.get_image.side_effect = itertools.cycle([image])
    with pytest.raises(
        ResourceTimeout,
        match=f"Timeout waiting for image {image.name} to become active.",
    ):
        wait_for_image_status(mock_conn, image, "active", interval=0, timeout=0)


def test_wait_for_image_status_immediate_success():
    """
    Test wait_for_image_status when the image already has the desired status.
    """
    mock_conn = MagicMock()
    image = MagicMock(id="123", name="test-image", status="active")
    result = wait_for_image_status(mock_conn, image, "active", interval=0, timeout=10)
    assert result == image
    mock_conn.image.get_image.assert_not_called()


def test_wait_for_image_status_error():
    """
    Test wait_for_image_status when the image status becomes error
    """
    mock_conn = MagicMock()
    image_pending = MagicMock(id="123", name="test-image", status="pending")
    image_error = MagicMock(id="123", name="test-image", status="error")
    mock_conn.image.get_image.side_effect = [
        image_pending,
        image_error,
    ]
    with pytest.raises(
        ResourceFailure, match=f"Image {image_error.name} failed to upload."
    ):
        wait_for_image_status(mock_conn, image_error, "active", interval=0, timeout=10)


def test_wait_for_migration_status_success():
    """
    Test wait_for_migration_status when it is a success
    """
    mock_conn = MagicMock()
    migration_pending = MagicMock(status="pending")
    migration_completed = MagicMock(status="completed")

    mock_conn.compute.migrations.side_effect = [
        iter([migration_pending]),
        iter([migration_pending]),
        iter([migration_completed]),
    ]

    result = wait_for_migration_status(
        mock_conn, "server_id", "completed", interval=0, timeout=10
    )
    assert result.status == "completed"


def test_wait_for_migration_status_timeout():
    """
    Test wait_for_migration_status when it hits the timeout
    """
    mock_conn = MagicMock()
    migration = MagicMock(status="pending")
    mock_conn.compute.migrations.side_effect = itertools.cycle([migration])

    with pytest.raises(
        ResourceTimeout, match="Timeout waiting for migration to become completed."
    ):
        wait_for_migration_status(
            mock_conn, "server_id", "completed", interval=0, timeout=0
        )


@pytest.mark.parametrize("bad_state", ["error", "failed"])
def test_wait_for_migration_status_error(bad_state):
    """
    Test wait_for_migration_status when the migration status becomes error
    """
    mock_conn = MagicMock()
    migration_pending = MagicMock(status="pending")
    migration_error = MagicMock(status=bad_state)
    mock_conn.compute.migrations.side_effect = [
        iter([migration_pending]),
        iter([migration_error]),
    ]
    with pytest.raises(ResourceFailure):
        wait_for_migration_status(
            mock_conn, "server_id", "completed", interval=0, timeout=10
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
