from typing import Optional, List, Dict
import logging
import requests
from apis.wazuh_api.structs.wazuh_account import WazuhAccount

logger = logging.getLogger(__name__)


def _query_agents(
    wazuh_token: str,
    endpoint: str,
    values: Optional[List] = None,
    query: Optional[str] = None,
) -> List:
    """
    Queries all agents in Wazuh to get a certain list of parameters
    for a specific query or filter

    :param wazuh_token: wazuh token to make API call with
    :param endpoint: Wazuh endpoint to query
    :param values: the list of variables to retrieve
    :type values: list
    :param query: the specific query against the Wazuh server
    :type query: str
    :return: the information in Wazuh for all agents
    :rtype: list
    """
    logger.info("Querying all agents for values %s and query %s", values, query)
    url = f"{endpoint}/agents"
    headers = {
        "Authorization": f"Bearer {wazuh_token}",
        "Content-Type": "application/json",
    }
    # we query Wazuh using pagination
    # we do not know how many agents there are
    out = []
    params = {
        "limit": 500,
        "offset": 0,
        "select": values,
        "q": query,
    }
    while True:
        try:
            response = requests.get(
                url, headers=headers, params=params, verify=False, timeout=60
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError("Failed to fetch data for all agents") from e
        data = response.json()
        items = data.get("data", {}).get("affected_items", [])
        # finished pagination loop
        if not items:
            break
        out.extend(items)
        # restart pagination loop with new offset
        params["offset"] += params["limit"]
    logger.info("Data for all agents fetched correctly")
    return out


def _wazuh_get_labels_for_agent(
    wazuh_token: str,
    endpoint: str,
    agent_id: str,
) -> List[Dict]:
    """
    get the entire list of labels associated to a given Agent ID

    :param wazuh_token: wazuh token to make API call with
    :type wazuh_token: str
    :param endpoint: Wazuh endpoint to query
    :type endpoint: str
    :param agent_id: the ID of the Wazuh Agent
    :type agent_id: str
    :return: a list of labels
    :rtype: List of Dictionaries
    """
    logger.info("Getting labels for agent %s", agent_id)
    url = f"{endpoint}/agents/{agent_id}/config/agent/labels"
    headers = {
        "Authorization": f"Bearer {wazuh_token}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=60)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch labels for agent {agent_id}") from e
    labels = response.json()["data"]["labels"]
    logger.info("Found %s labels for agent %s", len(labels), agent_id)
    return labels


def wazuh_get_server_id_from_label(
    wazuh_token: str,
    endpoint: str,
    agent_id: str,
) -> str:
    """
    extract the OpenStack Server ID from the list of labels
    associated to the corresponding Agent ID in Wazuh

    :param wazuh_token: wazuh token to make API call with
    :type wazuh_token: str
    :param endpoint: Wazuh endpoint to query
    :type endpoint: str
    :param agent_id: the ID of the Wazuh Agent
    :type agent_id: str
    :return: the Server ID
    :rtype: str
    """
    logger.info("getting the OpenStack Server ID for Agent ID %s", agent_id)
    labels = _wazuh_get_labels_for_agent(wazuh_token, endpoint, agent_id)
    for label in labels:
        if label["key"] == "openstack.uuid":
            server_id = label["value"]
            logger.info("found Server ID %s for Agent ID %s", server_id, agent_id)
            return server_id
    error_msg = f"No Server ID found for Agent ID {agent_id}"
    logger.error(error_msg)
    raise ValueError(error_msg)


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
    query = f"os.platform={os_name};os.major={os_version};status=active;group!=kolla"
    # we ensure we only get information about Servers and not Hypervisors
    # by adding conditions
    #   group!=kolla
    # to the query string
    data = _query_agents(
        wazuh_token, wazuh_account.wazuh_endpoint, values=["name"], query=query
    )

    server_id_list = []
    for agent in data:
        agent_id = agent["id"]
        try:
            server_id = wazuh_get_server_id_from_label(
                wazuh_token, wazuh_account.wazuh_endpoint, agent_id
            )
            server_id_list.append(server_id)
        except ValueError:
            logger.error("failed to get Server ID for Agent ID %s", agent_id)
    logger.info("returning a list of %s Server IDs", len(server_id_list))
    return server_id_list
