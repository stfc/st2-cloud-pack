import logging
import re
import urllib3
import requests

# Suppress insecure request warnings if using self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("WazuhClient")


# pylint: disable=too-few-public-methods
class WazuhClient:
    def __init__(self, pack_config):
        """
        gets the requires values to contact a Wazuh Server
        from the StackStorm configuration Dictionary pack_config

        :param pack_config: StackStorm configuration
        :type pack_config: dict
        """
        logger.info("Creating instance of WazuhClient")
        self.username = pack_config.get("wazuh_username")
        self.password = pack_config.get("wazuh_password")
        self.url = pack_config.get("wazuh_url")
        logger.info("Instance of WazuhClient created correctly")

    def _get_wazuh_token(self):
        """
        Authenticates with the Wazuh API and returns a JWT token.
        """
        logger.info("Getting a token")
        url = f"{self.url}/security/user/authenticate"
        try:
            # Wazuh uses Basic Auth to fetch the initial token
            response = requests.get(
                url, auth=(self.username, self.password), verify=False, timeout=60
            )
            response.raise_for_status()
            token = response.json().get("data", {}).get("token")
            logger.info("Token adquired correclty, returning it")
            return token
        except requests.exceptions.RequestException as e:
            logger.critical("Unable to retrieve a valid token: %s", e)
            raise e

    def _query_agents(self, values=None, query=None):
        """
        Queries all agents in Wazuh to get a certain list of parameters
        for a specific query or filter

        :param values: the list of variables to retrieve
        :type values: list
        :param query: the specific query against the Wazuh server
        :type query: str
        :return: the information in Wazuh for all agents
        :rtype: list
        """
        logger.info("Querying all agents for values %s and query %s", values, query)
        url = f"{self.url}/agents"
        token = self._get_wazuh_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        try:
            # we query Wazuh using pagination
            # we do not know how many agents there are
            out = []
            batch_size = 500
            offset = 0
            while True:
                params = {
                    "limit": batch_size,
                    "offset": offset,
                    "select": values,
                    "q": query,
                }
                response = requests.get(
                    url, headers=headers, params=params, verify=False, timeout=60
                )
                response.raise_for_status()
                data = response.json()
                items = data.get("data", {}).get("affected_items", [])
                if not items:
                    break
                out.extend(items)
                offset += batch_size
            logger.info("Data for all agents fetched correctly")
            return out
        except requests.exceptions.RequestException as e:
            logger.critical("Failed to fetch data for all agents: %s", e)
            raise e

    def get_all(self):
        return self._query_agents()

    def get_servers_for_os(self, os_name, os_version):
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
        data = self._query_agents(values=["name"], query=query)

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
