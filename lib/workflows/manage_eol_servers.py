import logging

from openstack.connection import Connection
from apis.openstack_api.openstack_server import set_metadata_foo_fixme, get_metadata_foo_fixme
from apis.openstack_query_api.user_queries import find_user_info
from apis.wazuh_api.wazuh import WazuhClient
from apis.elog_api.wazuh import ElogClient

logger = logging.getLogger(__name__)


def find_eol_servers(wazuh_client, os_name, os_version):
    """
    query Wazuh server to find the list of Servers running
    an EOL version of the OS

    :param wazuh_client: instance of a client class to query Wazuh
    :type wazuh_client: WazuhClient 
    :param elog_client: instance of a class to create records in ELOG 
    :type elog_client: WazuhClient 
    :param os_name: name of the OS we are interested on (e.g. ubuntu)
    :type os_name: str
    :param os_version: version of the OS we are interested on (e.g. 20)
    :type os_version: str
    :return: the list of Server IDs
    :rtype: list
    """
    logger.info("querying Wazuh to find servers running OS %s : %s", os_name, os_version)
    out = wazuh_client.get_servers_for_os(os_name, os_version)
    logger.info("Wazuh queried for servers running OS %s : %s", os_name, os_version)
    logger.info("returning %s Server ID", %len(out))
    return out


def manage_new_eol_server(conn, server_id):
    """
    Manage a single Server that we have just discovered
    is running an EOL version of the OS

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: ID of the Server running an EOL version of the OS
    :type server_id: str
    :return: None
    :rtype: None
    """
    logger.info("starting the process to manage server %s", server_id)
    logger.info("the server %s was never marked as running an EOL version of the OS", server_id)
    logger.info("marking the server %s as running an EOL version of the OS now", server_id)
    set_metadata_foo_fixme() # FIXME !!!
    logger.info("server %s marked as running an EOL version of the OS")
    username, email = find_user_info(server_id, conn._cloud_name)
    if not email:
        logger.error("there is no avaible information regarding the owner of Server %s", server_id)
    else:
        logger.info("notifiying the owner of server %s about it running an EOL version of the OS", server_id)
        email # FIXME !!!
        logger.info("owner of server %s notified about it running an EOL version of the OS", server_id)
    logger.info("process to manage server %s finished", server_id)


def manage_old_eol_server(conn, elog_client, server_id, metadata):
    """
    Manage a single Server that was already identified  
    is running an EOL version of the OS

    :param conn: openstack connection object
    :type conn: Connection
    :param elog_client: instance of a class to create records in ELOG 
    :type elog_client: WazuhClient 
    :param server_id: ID of the Server running an EOL version of the OS
    :type server_id: str
    :param metadata: the Server metadata with information regarding is OS
    :type metadata: str
    :return: None
    :rtype: None
    """
    logger.info("starting the process to manage server %s", server_id)
    logger.info("the server %s was already marked as running an EOL version of the OS", server_id)
    metadata_age = ... # FIXME !!! 
    if metadata_age < minimum_age: # FIXME !!!
        logger.info("the user of server %s was notified %s ago, nothing to do yet", server_id, metadata_age)
    else:
        shutoff_server(server_id) # FIXME !!!
        notify_user() # FIXME !!!
        elog() # FIXME !!!
    logger.info("process to manage server %s finished", server_id)


def manage_eol_server(conn, elog_client, server_id):
    """
    Manage a single Server running an EOL version of the OS

    - check if the Server is not marked 
      in that case:
      - mark it
      - notify user
    - if the Server was already marked
         - get how long ago
         - if not too long ago
           - pass
         - if long ago enough
           - shutoff the server
           - notify the user
           - elog it

    :param conn: openstack connection object
    :type conn: Connection
    :param server_id: ID of the Server running an EOL version of the OS
    :type server_id: str
    :return: None
    :rtype: None
    """
    logger.info("starting the process to manage server %s running an EOL version of the OS", server_id)
    metadata = get_metadata_foo_fixme() # FIXME !!!
    if not metadata:
        manage_new_eol_server(conn, server_id)
    else:
        manage_old_eol_server(conn, elog_client, server_id)
    logger.info("finished the process to manage server %s running an EOL version of the OS", server_id)


def eol_servers_workflow(conn, wazuh_client, elog_client, os_name, os_version):
    """
    Identify and manage all Server running an EOL version of the OS

    :param conn: openstack connection object
    :type conn: Connection
    :param wazuh_client: instance of a client class to query Wazuh
    :type wazuh_client: WazuhClient 
    :param elog_client: instance of a class to create records in ELOG 
    :type elog_client: WazuhClient 
    :param os_name: name of the OS we are interested on (e.g. ubuntu)
    :type os_name: str
    :param os_version: version of the OS we are interested on (e.g. 20)
    :type os_version: str
    :return: None
    :rtype: None
    """
    logger.info("starting workflow to identify and manage EOL Servers for %s : %s", os_name, os_version)
    server_list = find_eol_servers(wazuh_client, os_name, os_version)
    for server in server_list:
        manage_eol_server(conn, elog_client, server)
    logger.info("finished workflow to identify and manage EOL Servers for %s : %s", os_name, os_version)
