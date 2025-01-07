from datetime import datetime
from typing import Optional
from openstack.connection import Connection
from openstack.compute.v2.image import Image


def migrate_server(
    conn: Connection,
    server_id: str,
    dest_host: Optional[str] = None,
    live: bool = True,
) -> None:
    """
    Migrate a server to a new host
    :param conn: Openstack Connection
    :param server_id: Server ID to migrate
    :param dest_host: Optional host to migrate to, otherwise choosen by scheduler
    :param live: True for live migration
    """
    if not live:
        conn.compute.migrate_server(server=server_id, host=dest_host)
    else:
        conn.compute.live_migrate_server(
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
