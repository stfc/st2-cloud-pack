from typing import Tuple, Union, Dict, List, Callable

from openstack.network.v2.floating_ip import FloatingIP

from openstack_action import OpenstackAction
from openstack_api.dataclasses import QueryParams
from openstack_api.openstack_floating_ip import OpenstackFloatingIP
from openstack_api.openstack_network import OpenstackNetwork
from openstack_api.openstack_query import OpenstackQuery


class FloatingIPActions(OpenstackAction):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._network_api: OpenstackNetwork = config.get(
            "openstack_network_api", OpenstackNetwork()
        )
        self._fip_api: OpenstackFloatingIP = config.get(
            "openstack_floating_ip_api", OpenstackFloatingIP()
        )
        self._query_api: OpenstackQuery = config.get(
            "openstack_query_api", OpenstackQuery()
        )

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def floating_ip_get(
        self, cloud_account: str, ip_addr: str
    ) -> Tuple[bool, Union[FloatingIP, str]]:
        """
        Show floating ip information
        :param cloud_account: The account from the clouds configuration to use
        :param ip_addr: IP address to lookup
        :return: status, result if found else error message
        """
        found = self._network_api.get_floating_ip(cloud_account, ip_addr)
        to_return = found if found else "The requested floating IP could not be found"
        return bool(found), to_return

    def floating_ip_delete(self, ip_addr):
        """
        Delete floating ip_addr
        :param ip_addr: ip_addr id
        :return: (status (Bool), reason/output (String/Dict))
        """
        raise NotImplementedError("Deleting floating IPs are not supported")

    def floating_ip_create(
        self,
        cloud_account: str,
        network_identifier: str,
        project_identifier: str,
        number_to_create: int,
    ) -> Tuple[bool, List[FloatingIP]]:
        """
        Create floating IPs for a project
        :param cloud_account: The account from the clouds configuration to use
        :param network_identifier: ID or Name of network to allocate from,
        :param project_identifier: ID or Name of project to allocate to,
        :param number_to_create: Number of floating ips to create
        :return: List of all allocated floating IPs
        """
        created = self._network_api.allocate_floating_ips(
            cloud_account,
            network_identifier=network_identifier,
            project_identifier=project_identifier,
            number_to_create=number_to_create,
        )
        return bool(created), created

    # pylint:disable=too-many-arguments
    def floating_ip_list(
        self,
        cloud_account: str,
        query_preset: str,
        properties_to_select: List[str],
        group_by: str,
        return_html: bool,
        **kwargs,
    ) -> str:
        """
        Finds all floating ips belonging to a project (or all floating ips if project is empty)
        :param cloud_account: The account from the clouds configuration to use
        :param query_preset: The query to use when searching for floating ips
        :param properties_to_select: The list of properties to select and output from the found floating ips
        :param group_by: Property to group returned results - can be empty for no grouping
        :param return_html: When True tables returned are in html format
        :return: (String or Dictionary of strings) Table(s) of results grouped by the 'group_by' parameter
        """

        return self._fip_api.search(
            cloud_account=cloud_account,
            query_params=QueryParams(
                query_preset=query_preset,
                properties_to_select=properties_to_select,
                group_by=group_by,
                return_html=return_html,
            ),
            **kwargs,
        )

    def find_non_existent_floating_ips(
        self, cloud_account: str, project_identifier: str
    ):
        """
        Returns a dictionary containing the ids of projects along with a list of non-existent floating ips found
        within them
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A dictionary containing the non-existent server ids and their projects
        """
        return self._fip_api.find_non_existent_fips(
            cloud_account=cloud_account, project_identifier=project_identifier
        )

    def find_non_existent_projects(self, cloud_account: str):
        """
        Returns a dictionary containing the ids of non-existent projects along with a list of floating ips that
        refer to them
        :param cloud_account: The associated clouds.yaml account
        :return: A dictionary containing the non-existent server ids and their projects
        """
        return self._fip_api.find_non_existent_projects(cloud_account=cloud_account)
