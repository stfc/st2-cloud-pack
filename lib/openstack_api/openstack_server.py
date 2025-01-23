from datetime import datetime
from typing import Optional
from openstack.connection import Connection
from openstack.compute.v2.image import Image


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
    if server_status == "SHUTOFF":
        return conn.compute.migrate_server(server=server_id, host=dest_host)
    return conn.compute.live_migrate_server(
        server=server_id, host=dest_host, block_migration=True
    )


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

    # Make VM's project image owner
    conn.image.update_image(image, owner=project_id)

    return image


def build_server(
    conn: Connection,
    server_name: str,
    flavor_name: str,
    image_name: str,
    network_name: str,
    hypervisor_hostname: Optional[str] = None,
):
    flavor = conn.compute.find_flavor(flavor_name)
    image = conn.image.find_image(image_name)
    network = conn.network.find_network(network_name)

    server = conn.compute.create_server(
        **{
            "name": server_name,
            "imageRef": image.id,
            "flavorRef": flavor.id,
            "networks": [{"uuid": network.id}],
            "hypervisor": hypervisor_hostname,
        }
    )

    conn.compute.wait_for_server(
        server, status="ACTIVE", failures=None, interval=5, wait=300
    )
