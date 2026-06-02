import logging
import re

from openstack.connection import Connection
from apis.openstack_query_api.server_queries import find_servers_on_hv
from apis.openstack_api.openstack_server import shutoff_server_list

logger = logging.getLogger(__name__)


def shutdown_all_servers_in_hypervisor(
    conn: Connection,
    hypervisor_name: str,
) -> None:
    """
    Shutdown all servers in a hypervisor

    :param conn: openstack connection object
    :type conn: Connection
    :param hypervisor_name: Hostname of the hypervisor
    :type hypervisor_name: str
    :return: None
    :rtype: None
    """
    logger.info("Attempting to shut down all servers is hypervisor %s", hypervisor_name)
    # 1st we ensure the hypervisor name is correct
    # remove potential leading/trailing whitespaces
    hypervisor_name = hypervisor_name.strip()
    if not hypervisor_name:
        logger.error("Hypervisor hostname is empty")
        raise ValueError("Hypervisor hostname is empty")
    # check no special characters are included
    pattern = re.compile(r"^[A-Za-z0-9._-]+$")
    # Compile a regular expression that allows:
    # - letters (a–z, A–Z)
    # - digits (0–9)
    # - dot (.)
    # - underscore (_)
    # - dash (-)
    if not pattern.fullmatch(hypervisor_name):
        logger.error("Hypervisor hostname cannot include special characters")
        raise ValueError("Hypervisor hostname cannot include special characters")
    # if everything is OK with the hostname we can proceed

    # we get the entire list of server in this hypervisor
    servers_query = find_servers_on_hv(
        cloud_account=conn.name,
        hypervisor_name=hypervisor_name,
        from_projects=None,
        webhook=None,
    )
    # servers_query is a ServerQuery object
    # we extract the information we need from it
    server_id_list = [server.id for server in servers_query.to_objects()]
    if not server_id_list:
        logger.info("No server found in hypervisor %s", hypervisor_name)
    else:
        logger.info("Found all servers for hypervisor %s", hypervisor_name)
        # we shut them down
        try:
            shutoff_server_list(conn, server_id_list)
            logger.info("All servers for hypervisor %s shut down", hypervisor_name)
        except Exception as ex:
            logger.error("Exception captured when trying to shut down servers: %s", ex)
            raise ex
