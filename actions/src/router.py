from st2common.runners.base_action import Action
import openstack
import random
from openstack_action import OpenstackAction

class Router(OpenstackAction):

    def __init__(self, *args, **kwargs):
        """ constructor class """
        super().__init__(*args, **kwargs)

        # lists possible functions that could be run as an action
        self.func = {
            "router_create": self.router_create,
            "router_add_interface": self.router_add_interface,
        }

    def router_create(self, **kwargs):
        """
        Create openstack router for project
        :param kwargs: project (String): Name or ID, external_gateway (String): Name or ID,  (other_args - see action definintion yaml file for details)
        :return: (status (Bool), reason (String))
        """
        new_kwargs = {k:v for k, v in kwargs.items() if k not in ["project", "external_gateway"]}

        project_id = self.find_resource_id(kwargs["project"], self.conn.identity.find_project)
        if not project_id:
            return False, "Project not found with Name or ID {}".format(kwargs["project"])

        external_gateway_id = self.find_resource_id(kwargs["external_gateway"], self.conn.network.find_network)
        if not external_gateway_id:
            return False, "Network (External Gateway) not found with Name or ID {}".format(kwargs["project"])
        try:
            router = self.conn.network.create_router(project_id=project_id, external_gateway_info={"network_id":external_gateway_id}, **new_kwargs)
        except Exception as e:
            return False, "Router Creation Failed {}".format(e)
        return True, router

    def router_add_interface(self, **kwargs):
        """
        Add interface to Openstack router
        :param kwargs: router (String): ID or Name, subnet (String): ID or Name, port (String): ID or Name
        :return: (status (Bool), reason (String))
        """

        # requires either subnet_id or port_id
        subnet_id, port_id = None, None

        # get router id
        router_id = self.find_resource_id(kwargs["router"], self.conn.network.find_router)
        if not router_id:
            return False, "Router not found with Name or ID {}".format(kwargs["router"])

        # if subnet provided - get subnet id
        if "subnet" in kwargs.keys():
            subnet_id = self.find_resource_id(kwargs["subnet"], self.conn.network.find_subnet)
            if not router_id:
                return False, "Router not found with Name or ID {}".format(kwargs["router"])

        # if port provided - get port id
        if "port" in kwargs.keys():
            port_id = self.find_resource_id(kwargs["port"], self.conn.network.find_port)
            if not port_id:
                return False, "Port not found with Name or ID {}".format(kwargs["port"])

        try:
            router = self.conn.network.add_interface_to_router(router=router_id, subnet_id=subnet_id, port_id=port_id)
        except Exception as e:
            return False, "Adding Router Interface Failed {}".format(e)
        return True, router
