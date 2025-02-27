from datetime import datetime
import time
from typing import Optional
from openstack.connection import Connection
from openstack.compute.v2.image import Image
from openstack.compute.v2.server import Server
from openstack.exceptions import ResourceFailure, ResourceTimeout


def snapshot_and_migrate_server(
    conn: Connection,
    server_id: str,
    server_status: str,
    flavor_id: str,
    snapshot: bool,
    dest_host: Optional[str] = None,
) -> None:
    """
    Optionally snapshot a server and then migrate it to a new host
    :param conn: Openstack Connection
    :param server_id: Server ID to migrate
    :param server_status: Status of machine to migrate - must be ACTIVE or SHUTOFF
    :param flavor_name: Server flavor name
    :param dest_host: Optional host to migrate to, otherwise chosen by scheduler
    """
    if flavor_id.startswith("g-"):
        raise ValueError(
            f"Attempted to move GPU flavor, {flavor_id}, which is not allowed!"
        )
    if server_status not in ["ACTIVE", "SHUTOFF"]:
        raise ValueError(
            f"Server status: {server_status}. The server must be ACTIVE or SHUTOFF to be migrated"
        )
    if snapshot:
        snapshot_server(conn=conn, server_id=server_id)
    server = conn.compute.get_server(server_id)
    if server_status == "SHUTOFF":
        conn.compute.migrate_server(server=server_id, host=dest_host)
        conn.compute.wait_for_server(server, status="VERIFY_RESIZE")
        conn.compute.confirm_server_resize(server_id)
        wait_for_migration_status(conn, server_id, "confirmed")
    if server_status == "ACTIVE":
        conn.compute.live_migrate_server(
            server=server_id, host=dest_host, block_migration=True
        )
        wait_for_migration_status(conn, server_id, "completed")


def snapshot_server(conn: Connection, server_id: str) -> Image:
    """
    Creates a snapshot image of a server
    :param conn: Openstack connection
    :param server_id: ID of server to snapshot
    :return: Snapshot Image
    """
    current_time = datetime.now().strftime("%d-%m-%Y-%H%M")

    project_id = conn.compute.find_server(server_id, all_projects=True).project_id
    image = conn.compute.create_server_image(
        server=server_id, name=f"{server_id}-{current_time}", wait=True, timeout=3600
    )
    wait_for_image_status(conn, image, "active")
    # Make VM's project image owner
    conn.image.update_image(image, owner=project_id)

    return image


def wait_for_image_status(conn: Connection, image, status, interval=5, timeout=600):
    """
    Waits for the status of the image to be the selected status
    :param conn: Openstack connection
    :param image: The Image object
    :param status: The status of the image that is required
    :param interval:How long to wait between checks
    :param timeout: Timeout of the function
    """
    if image.status == status:
        return image
    start_time = time.time()
    while time.time() - start_time < timeout:
        image = conn.image.get_image(image.id)
        if image.status == status:
            return image
        if image.status == "error":
            raise ResourceFailure(f"Image {image.name} failed to upload.")
        time.sleep(interval)
    raise ResourceTimeout(f"Timeout waiting for image {image.name} to become {status}.")


def wait_for_migration_status(
    conn: Connection, server_id, status, interval=5, timeout=600
):
    """
    Waits for the status of the migration to be the selected status
    :param conn: Openstack connection
    :param server_id: The ID of the server where the migrations are from
    :param status: The status of the migration that is required
    :param interval:How long to wait between checks
    :param timeout: Timeout of the function
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        migration = next(conn.compute.migrations(instance_uuid=server_id))
        if migration.status == status:
            return migration
        if migration.status in ["error", "failed"]:
            raise ResourceFailure(migration)
        time.sleep(interval)
    raise ResourceTimeout(f"Timeout waiting for migration to become {status}.")


def build_server(
    conn: Connection,
    server_name: str,
    flavor_name: str,
    image_name: str,
    network_name: str,
    hypervisor_hostname: Optional[str] = None,
    delete_on_failure: Optional[bool] = False,
) -> Server:
    """
    Builds a server, with option to specify a hypervisor

    :param conn: openstack connection object
    :type conn: Connection
    :param server_name: Name of server
    :type server_name: str
    :param flavor_name: Flavor to use for server
    :type flavor_name: str
    :param image_name: Image to use for server
    :type image_name: str
    :param network_name: Network name for server
    :type network_name: str
    :param hypervisor_hostname: Optional, hypervisor to build server on
    :type hypervisor_hostname:
    :return: Server instance
    :rtype: Server
    """
    flavor = conn.compute.find_flavor(flavor_name)
    image = conn.image.find_image(image_name)
    network = conn.network.find_network(network_name)

    server = conn.compute.create_server(
        **{
            "name": server_name,
            "imageRef": image.id,
            "flavorRef": flavor.id,
            "networks": [{"uuid": network.id}],
            "host": hypervisor_hostname,
            "openstack_api_version": "2.74",
        }
    )
    try:
        conn.compute.wait_for_server(
            server, status="ACTIVE", failures=None, interval=5, wait=300
        )
    except (ResourceTimeout, ResourceFailure) as e:
        if delete_on_failure:
            conn.compute.delete_server(server, force=True)
        raise ResourceFailure(server.fault) from e
    return server


def delete_server(
    conn: Connection, server_id: str, force: Optional[bool] = False
) -> None:
    """
    Delete a server

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: ID of server to delete
    :type server_id: str
    :param force: Option to force delete server
    :type force: bool
    :return: None
    :rtype: None
    """
    server = conn.compute.find_server(server_id)
    conn.compute.delete_server(server, force)

    conn.compute.wait_for_delete(server, interval=5, wait=300)
