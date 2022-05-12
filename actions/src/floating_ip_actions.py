from typing import Tuple, Union, Dict, List

from openstack.network.v2.floating_ip import FloatingIP

from openstack_action import OpenstackAction
from openstack_api.openstack_network import OpenstackNetwork


class FloatingIPActions(OpenstackAction):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._api: OpenstackNetwork = config.get("openstack_api", OpenstackNetwork())

        # lists possible functions that could be run as an action
        self.func = {
            "floating_ip_create": self.floating_ip_create,
            "floating_ip_delete": self.floating_ip_delete,
            "floating_ip_get": self.floating_ip_get
            # floating_ip_update
        }

    def floating_ip_get(
        self, cloud_account: str, ip_addr: str
    ) -> Tuple[bool, Union[FloatingIP, str]]:
        """
        Show floating ip information
        :param cloud_account: The account from the clouds configuration to use
        :param ip_addr: IP address to lookup
        :return: status, result if found else error message
        """
        found = self._api.get_floating_ip(cloud_account, ip_addr)
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
        created = self._api.allocate_floating_ips(
            cloud_account,
            network_identifier=network_identifier,
            project_identifier=project_identifier,
            number_to_create=number_to_create,
        )
        return bool(created), created
