import logging

from apis.openstack_query_api.server_queries import find_shutoff_servers
from tabulate import tabulate

logger = logging.getLogger(__name__)


def find_shutdown_servers(
    conn,
    minimum_days,
):
    """
    Find servers in SHUTOFF state

    :param conn: openstack connection object
    :type conn: Connection
    :param minimum_days: minimum number of days a Server must be SHUTOFF to be included in the results
    :type minimum_days: int
    :return: the list of Servers found
    :rtype: list
    """
    logger.info(
        "Finding all servers in SHUTOFF state for longer than %s days", minimum_days
    )

    servers_q = find_shutoff_servers(
        cloud_account=conn.name, days_threshold=minimum_days
    )
    # servers_q is an object of class ServerQuery
    servers = servers_q.to_objects()

    # create a table with results
    table_headers = ["Server Name", "Server ID"]
    table_data = [[server.name, server.id] for server in servers]
    table = tabulate(table_data, headers=table_headers, tablefmt="grid")
    print(table)
    return servers
