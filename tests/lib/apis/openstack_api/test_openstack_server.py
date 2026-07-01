import itertools
from datetime import datetime
from typing import Tuple, Any
from unittest.mock import MagicMock, patch, PropertyMock

import pytest
from apis.openstack_api.openstack_server import (
    build_server,
    delete_server,
    snapshot_and_migrate_server,
    snapshot_server,
    wait_for_image_status,
    wait_for_migration_status,
    shutoff_server,
)
from openstack.exceptions import ResourceFailure, ResourceTimeout


@pytest.fixture(autouse=True)
def patch_sleep():
    with patch("time.sleep", return_value=None):
        yield


@pytest.mark.parametrize("dest_host", [None, "hv01"])
@patch("apis.openstack_api.openstack_server.snapshot_server")
@patch("apis.openstack_api.openstack_server.wait_for_migration_status")
@patch("time.sleep")
def test_active_migration(
    mock_time, mock_wait_for_migration_status, mock_snapshot_server, dest_host
):
    """
    Test migration when the status of the server is ACTIVE and the destination host is supplied
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server = MagicMock()
    mock_server.id = mock_server_id
    mock_server.flavor.name = "l3.nano"
    mock_server.flavor.vcpus = 2
    mock_server.status = "ACTIVE"
    mock_connection.compute.get_server.return_value = mock_server
    snapshot_and_migrate_server(
        conn=mock_connection,
        server_id=mock_server_id,
        dest_host=dest_host,
        snapshot=True,
        live_migration=True,
    )
    mock_snapshot_server.assert_called_once_with(
        conn=mock_connection, server_id=mock_server_id
    )
    mock_time.assert_called_once_with(10)
    mock_connection.compute.live_migrate_server.assert_called_once_with(
        server=mock_server_id, host=dest_host, block_migration=True
    )
    mock_wait_for_migration_status.assert_called_once_with(
        mock_connection, mock_server_id, "completed"
    )
    mock_connection.compute.migrate_server.assert_not_called()


def _migration_side_effect_generator(
    mock_server, mock_connection, return_values: Tuple[Any, Any]
) -> None:
    """
    Instruments a fake server to always return the first value of a tuple until migrate is called
    after it will always return the second value of the tuple
    """

    class MigrateAPIFake:
        def __init__(self):
            self.called = False

        def callable_migration(self, *_, **__):
            self.called = True

        def return_val(self, *_, **__):
            return return_values[0] if not self.called else return_values[1]

    api_fake = MigrateAPIFake()

    # Patch in a side effect of calling migrate_server will cause mock_server.status to update to VERIFY_RESIZE
    mock_connection.compute.migrate_server.side_effect = api_fake.callable_migration
    type(mock_server).status = PropertyMock(side_effect=api_fake.return_val)
    mock_connection.compute.get_server.return_value = mock_server


@patch("apis.openstack_api.openstack_server.snapshot_server")
@patch("apis.openstack_api.openstack_server.wait_for_migration_status")
def test_active_cold_migration(_, __):
    """
    Tests that active VMs are also be migratable
    """
    mock_connection = MagicMock()
    mock_server = MagicMock()

    _migration_side_effect_generator(
        mock_server, mock_connection, return_values=("ACTIVE", "VERIFY_RESIZE")
    )
    snapshot_and_migrate_server(
        conn=mock_connection,
        server_id="",
        snapshot=False,
        live_migration=False,
    )

    # If we see migrate server called we can assume it's done the same calls as shutoff any rely on that unit test
    mock_connection.compute.migrate_server.assert_called_once()


@pytest.mark.parametrize("dest_host", [None, "hv01"])
@patch("apis.openstack_api.openstack_server.snapshot_server")
@patch("apis.openstack_api.openstack_server.wait_for_migration_status")
def test_shutoff_migration(
    mock_wait_for_migration_status, mock_snapshot_server, dest_host
):
    """
    Test migration when the status of the server is SHUTOFF and the destination host is supplied
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server = MagicMock()
    mock_server.id = mock_server_id
    mock_server.flavor.name = "l3.nano"
    mock_server.flavor.vcpus = 2

    _migration_side_effect_generator(
        mock_server,
        mock_connection,
        # Mixed case intentional
        return_values=("SHUToff", "VERIFY_RESIZE"),
    )

    snapshot_and_migrate_server(
        conn=mock_connection,
        server_id=mock_server_id,
        dest_host=dest_host,
        snapshot=True,
        live_migration=False,
    )

    mock_snapshot_server.assert_called_once_with(
        conn=mock_connection, server_id=mock_server_id
    )
    mock_connection.compute.live_migrate_server.assert_not_called()
    mock_connection.compute.migrate_server.assert_called_once_with(
        server=mock_server_id, host=dest_host
    )
    mock_connection.compute.wait_for_server.assert_called_once_with(
        mock_server, status="VERIFY_RESIZE", wait=10
    )
    mock_connection.compute.confirm_server_resize.assert_called_once_with(
        mock_server_id
    )
    mock_wait_for_migration_status.assert_called_once_with(
        mock_connection, mock_server_id, "finished"
    )


@patch("apis.openstack_api.openstack_server.snapshot_server")
@patch("apis.openstack_api.openstack_server.wait_for_migration_status")
def test_invalid_status_after_migration(_, __):
    """
    Tests if the migration is marked finished but the VM moves into an error or unknown state instead of VERIFY_RESIZE
    """
    mock_connection = MagicMock()
    mock_server = MagicMock()

    _migration_side_effect_generator(
        mock_server, mock_connection, return_values=("ACTIVE", "ERROR")
    )
    with pytest.raises(RuntimeError):
        snapshot_and_migrate_server(
            conn=mock_connection,
            server_id="",
            snapshot=False,
            live_migration=False,
        )

    mock_connection.compute.migrate_server.assert_called_once()
    mock_connection.compute.confirm_resize.assert_not_called()

    # Also confirm we error on a weird state like ACTIVE which migrate should not go to
    _migration_side_effect_generator(
        mock_server, mock_connection, return_values=("ACTIVE", "ACTIVE")
    )
    with pytest.raises(RuntimeError):
        snapshot_and_migrate_server(
            conn=mock_connection,
            server_id="",
            snapshot=False,
            live_migration=False,
        )


@patch("apis.openstack_api.openstack_server.snapshot_server")
@patch("apis.openstack_api.openstack_server.wait_for_migration_status")
def test_active_migration_failed_wait_for_status(
    mock_wait_for_migration_status, mock_snapshot_server
):
    """
    Test migration when the status of migration raises an error
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server = MagicMock()
    mock_server.id = mock_server_id
    mock_server.flavor.name = "l3.nano"
    mock_server.flavor.vcpus = 2
    mock_server.status = "ACTIVE"
    mock_connection.compute.get_server.return_value = mock_server

    mock_wait_for_migration_status.side_effect = ResourceTimeout
    with pytest.raises(ResourceTimeout):
        snapshot_and_migrate_server(
            conn=mock_connection,
            server_id=mock_server_id,
            dest_host=None,
            snapshot=True,
            live_migration=True,
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


@patch("apis.openstack_api.openstack_server.snapshot_server")
@patch("apis.openstack_api.openstack_server.wait_for_migration_status")
def test_no_snapshot_migration(mock_wait_for_migration_status, mock_snapshot_server):
    """
    Test migration with no snapshot
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server = MagicMock()
    mock_server.id = mock_server_id
    mock_server.flavor.name = "l3.nano"
    mock_server.flavor.vcpus = 2
    mock_server.status = "ACTIVE"
    mock_connection.compute.get_server.return_value = mock_server

    snapshot_and_migrate_server(
        conn=mock_connection,
        server_id=mock_server_id,
        snapshot=False,
        live_migration=True,
    )
    mock_snapshot_server.assert_not_called()
    mock_connection.compute.live_migrate_server.assert_called_once_with(
        server=mock_server_id, host=None, block_migration=True
    )
    mock_wait_for_migration_status.assert_called_once_with(
        mock_connection, mock_server_id, "completed"
    )


@patch("apis.openstack_api.openstack_server.snapshot_server")
def test_migration_fail(mock_snapshot_server):
    """
    Test failure of migration when the status is not ACTIVE or SHUTOFF
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server = MagicMock()
    mock_server.id = mock_server_id
    mock_server.flavor.name = "l3.nano"
    mock_server.flavor.vcpus = 2
    mock_server.status = "ERROR"
    mock_connection.compute.get_server.return_value = mock_server

    with pytest.raises(
        ValueError,
        match="Server status: ERROR. The server must be ACTIVE or SHUTOFF to be migrated",
    ):
        snapshot_and_migrate_server(
            conn=mock_connection,
            server_id=mock_server_id,
            snapshot=False,
            live_migration=True,
        )
    mock_snapshot_server.assert_not_called()
    mock_connection.compute.live_migrate_server.assert_not_called()
    mock_connection.compute.migrate_server.assert_not_called()


@patch("apis.openstack_api.openstack_server.wait_for_image_status")
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
        name=f"stackstorm-{mock_server_id}-{current_time}",
        wait=True,
        timeout=21600,  # 6 Hours
    )
    mock_wait_for_image_status.assert_called_once_with(
        mock_connection, mock_image, "active"
    )
    mock_connection.image.update_image.assert_called_once_with(
        mock_image, owner=mock_project_id
    )


@pytest.mark.parametrize(
    "flavor_name,flavor_vcpu",
    [("g-a100-80gb-2022.x2", 30), ("f-xilinxu200.x1", 28), ("l3.large", 124)],
)
def test_raise_invalid_migration(flavor_name, flavor_vcpu):
    """
    Test migration of gpu flavor raises error
    """
    mock_connection = MagicMock()
    mock_server_id = "server1"
    mock_server = MagicMock()
    mock_server.id = mock_server_id
    mock_server.flavor.name = flavor_name
    mock_server.flavor.vcpus = flavor_vcpu
    mock_server.status = "ACTIVE"
    mock_connection.compute.get_server.return_value = mock_server

    with pytest.raises(ValueError):
        snapshot_and_migrate_server(
            conn=mock_connection,
            server_id=mock_server_id,
            dest_host=None,
            snapshot=False,
            live_migration=True,
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
        mock_server, status="ACTIVE", failures=None, interval=5, wait=3600
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
        mock_server, status="ACTIVE", failures=None, interval=5, wait=3600
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
        mock_server, status="ACTIVE", failures=None, interval=5, wait=3600
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
        mock_server, interval=5, wait=3600
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
        mock_server, interval=5, wait=3600
    )


def test_shutoff_server_propagates_resource_failure():
    """
    test that an Exception is raised when the servers goes
    into ERROR status
    """
    mock_server = MagicMock()
    mock_server.id = "server-123"
    mock_server.status = "ACTIVE"

    expected_exception = ResourceFailure("Any generic error message can go here")

    mock_conn = MagicMock()
    mock_conn.compute.find_server.return_value = mock_server

    mock_conn.compute.wait_for_status.side_effect = expected_exception

    with pytest.raises(ResourceFailure) as exc_info:
        shutoff_server(mock_conn, "server-123")

    assert exc_info.value is expected_exception
