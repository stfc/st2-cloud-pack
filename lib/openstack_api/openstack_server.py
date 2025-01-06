from datetime import datetime
from typing import Optional
from openstack.connection import Connection
from openstack.compute.v2.image import Image


def snapshot_and_migrate_server(
    conn: Connection,
    server_id: str,
    server_status: str,
    snapshot: bool,
    dest_host: Optional[str] = None,
) -> None:
    """
    Optionally snapshot a server and then migrate it to a new host
    :param conn: Openstack Connection
    :param server_id: Server ID to migrate
    :param server_status: Status of machine to migrate - must be ACTIVE or SHUTOFF
    :param dest_host: Optional host to migrate to, otherwise chosen by scheduler
    """
    if snapshot:
        snapshot_server(conn=conn, server_id=server_id)
    if server_status not in ["ACTIVE", "SHUTOFF"]:
        raise ValueError(
            f"Server status: {server_status}. The server must be ACTIVE or SHUTOFF to be migrated"
        )
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
        server=server_id, name=f"{server_id}-{current_time}", wait=True, timeout=300
    )

    # Make VM's project image owner
    conn.image.update_image(image, owner=project_id)

    return image
