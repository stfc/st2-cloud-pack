from typing import Tuple, Dict, Union, Callable

from openstack.exceptions import ResourceNotFound
from openstack.network.v2.router import Router

from openstack_action import OpenstackAction
from openstack_api.openstack_network import OpenstackNetwork
from structs.router_details import RouterDetails


class RouterActions(OpenstackAction):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._api: OpenstackNetwork = config.get("openstack_api", OpenstackNetwork())

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    # pylint: disable=too-many-arguments
    def router_create(
        self,
        cloud_account: str,
        project_identifier: str,
        router_name: str,
        router_description: str,
        external_gateway: str,
        is_distributed: bool,
        is_ha: bool,
    ) -> Tuple[bool, Router]:
        """
        Create openstack router for project
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: Name or ID of the Openstack Project
        :param router_name: The new router name
        :param router_description: The new router's description
        :param is_distributed: Is the new router distributed
        :param is_ha: Is the new router high availability
        :param external_gateway: Name or ID of the external gateway the router should use
        :return: Status, new router object
        """
        router = self._api.create_router(
            cloud_account,
            RouterDetails(
                project_identifier=project_identifier,
                router_name=router_name,
                router_description=router_description,
                external_gateway=external_gateway,
                is_distributed=is_distributed,
                is_ha=is_ha,
            ),
        )
        return bool(router), router

    def router_add_interface(
        self,
        cloud_account: str,
        project_identifier: str,
        router_identifier: str,
        subnet_identifier: str,
    ) -> Tuple[bool, Router]:
        """
        Add interface to Openstack router
        :param cloud_account: The account from the clouds configuration to use
        :param router_identifier: ID or Name of the router
        :param subnet_identifier: ID or Name of the subnet
        :return: status, associated router
        """
        router = self._api.add_interface_to_router(
            cloud_account, project_identifier, router_identifier, subnet_identifier
        )
        return bool(router), router

    def router_get(
        self, cloud_account: str, project_identifier: str, router_identifier: str
    ) -> Tuple[bool, Union[Router, str]]:
        """
        Gets a router in the specified project with the given name or ID
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: The project name or ID to search in
        :param router_identifier: The name or ID of the router
        :return: status, Router or error message
        """
        found = self._api.get_router(
            cloud_account, project_identifier, router_identifier
        )
        to_return = found if found else "The specified router could not be found"
        return bool(found), to_return

    def router_remove_interface(self, router, subnet, port):
        """
        Remove interface to Openstack router
        :param router: (String) ID or Name
        :param subnet: (String) ID or Name,
        :param port: (String) ID or Name
        :return: (status (Bool), reason (String))
        """

        # requires either subnet_id or port_id
        subnet_id, port_id = None, None

        # get router id
        router_id = self.find_resource_id(router, self.conn.network.find_router)
        if not router_id:
            return False, f"Router not found with Name or ID {router}"

        # if subnet provided - get subnet id
        if subnet:
            subnet_id = self.find_resource_id(subnet, self.conn.network.find_subnet)
            if not router_id:
                return False, f"Router not found with Name or ID {subnet}"

        # if port provided - get port id
        if port:
            port_id = self.find_resource_id(port, self.conn.network.find_port)
            if not port_id:
                return False, f"Port not found with Name or ID {port}"

        try:
            router = self.conn.network.remove_interface_from_router(
                router=router_id, subnet_id=subnet_id, port_id=port_id
            )
        except ResourceNotFound as err:
            return False, f"Removing Router Interface Failed {err}"
        return True, router

    def router_show(self, router):
        """
        Show router properties
        :param router: Name or ID
        :return: (status (Bool), reason (String))
        """
        try:
            router = self.conn.network.find_router(router, ignore_missing=False)
        except ResourceNotFound as err:
            return False, f"Router not found {repr(err)}"
        return True, router

    def router_delete(self, router):
        """
        Delete router
        :param router: Name or ID
        :return: (status (Bool), reason (String))
        """
        raise NotImplementedError

    def router_update(self, router, **update_kwargs):
        """
        Update router properties
        :param router: Name or ID
        :param update_kwargs: see action definintion yaml file for details)
        :return: (status (Bool), reason (String))
        """
        raise NotImplementedError
