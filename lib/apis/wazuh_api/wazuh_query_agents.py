from typing import Optional, List
import logging
import requests

logger = logging.getLogger(__name__)


def query_agents(
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
            raise RuntimeError("Failed to fetch data for all agents: %s") from e
        data = response.json()
        items = data.get("data", {}).get("affected_items", [])
        # finished pagination loop
        if not items:
            break
        out.extend(items)
        # restart pagination loop with new offset
        params["offset"] += params["BATCH_SIZE"]
    logger.info("Data for all agents fetched correctly")
    return out
