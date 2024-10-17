from typing import Optional

from openstack.connection import Connection
from openstack_api.openstack_server import migrate_server, snapshot_server


def server_migration(
    conn: Connection,
    server_id: str,
    destination_host: Optional[str] = None,
    live: bool = True,
) -> None:
    """Docstring for migrate_server

    :param cloud_account: Cloud account to use for openstack interaction
    :type cloud_account: str
    :param server_id: Server ID of server to migrate
    :type server_id: str
    :param destination_host: Optional, host to migrate server to
    :type destination_host: str
    :param live: True to use live migration
    :type live: bool
    """
    snapshot_server(conn, server_id)

    migrate_server(conn, server_id=server_id, dest_host=destination_host, live=live)
