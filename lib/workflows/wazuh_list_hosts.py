import logging
import re
from apis.wazuh_api.structs.wazuh_account import WazuhAccount
from lib.apis.wazuh_api.wazuh_query_agents import query_agents

logger = logging.getLogger(__name__)


def wazuh_list_servers_by_os(
    wazuh_account: WazuhAccount, os_name: str, os_version: str
):
    """
    query the Wazuh server to get data only for
    VMs running a specific version of the OS

    :param os_name: the OS name
    :type os_name: str
    :param os_version: the OS version
    :type os_version: str
    :return: the list of VM IDs
    :rtype: list
    """
    wazuh_token = wazuh_account.get_wazuh_token()
    logger.info(
        "query Wazuh for Servers running OS name %s and %s version",
        os_name,
        os_version,
    )
    query = f"os.platform={os_name};os.major={os_version};status=active;group!=kolla;group!=quattor"
    # we ensure we only get information about Servers and not Hypervisors
    # by adding conditions
    #   group!=kolla
    #   group!=quattor
    # to the query string
    data = query_agents(wazuh_token, wazuh_account.url, values=["name"], query=query)

    # extract the Server ID from the fetched data
    # the variable "name" for OpenStack Servers looks like this:
    #   host-192-168-231-139.openstacklocal-001682d2-79a2-41b9-af7f-c553f7d67b0d
    # we need to extract the ID from there
    uuid_re = re.compile(
        r"([0-9a-fA-F]{8}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{12})$"
    )
    server_id_l = []
    for server in data:
        name = server["name"]
        match = uuid_re.search(name)
        if match:
            server_id = match.group(1)
            server_id_l.append(server_id)
        else:
            logger.error("failed to extract Server ID from %s", server)

    logger.info("returning a list of %s Server IDs", len(server_id_l))
    return server_id_l
