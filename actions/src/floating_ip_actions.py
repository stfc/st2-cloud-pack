from typing import Tuple, Dict, List, Callable

from openstack.network.v2.floating_ip import FloatingIP

from openstack_action import OpenstackAction
from openstack_api.openstack_network import OpenstackNetwork


class FloatingIPActions(OpenstackAction):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._network_api: OpenstackNetwork = config.get(
            "openstack_network_api", OpenstackNetwork()
        )

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

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
