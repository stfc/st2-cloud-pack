import random
import re

from openstack.exceptions import ResourceNotFound

from openstack_action import OpenstackAction


class Subnet(OpenstackAction):
    def __init__(self, *args, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)

        # lists possible functions that could be run as an action
        self.func = {
            "subnet_create": self.subnet_create,
            "subnet_update": self.subnet_update,
            "subnet_delete": self.subnet_delete,
            "subnet_show": self.subnet_show,
        }

    def subnet_delete(self, subnet):
        """
        Delete a subnet
        :param subnet: Name or ID
        :return: (status (Bool), reason/output (String/Dict))
        """
        raise NotImplementedError

    def subnet_update(self, subnet, **update_kwargs):
        """
        Update a subnet
        :param subnet: Name or ID
        :param update_kwargs: update properties
        :return: (status (Bool), reason/output (String/Dict))
        """
        raise NotImplementedError

    def subnet_show(self, subnet):
        """
        Show subnet properties
        :param subnet: Name or ID
        :return: (status (Bool), reason/output (String/Dict))
        """
        try:
            subnet = self.conn.network.find_subnet(subnet, ignore_missing=False)
        except ResourceNotFound as err:
            return False, f"Subnet not found {repr(err)}"
        return True, subnet

    def subnet_create(self, network, **subnet_kwargs):
        """
        Create a Subnet on a Network
        :param network: (String) ID or Name
        :param subnet_kwargs: (other_args - see action definintion yaml file for details)
        :return: (status (Bool), reason/output (String/Dict))
        """

        # calculate and choose random available gateway ip_addr
        currently_used = set(
            subnet["gateway_ip"].split(".")[2]
            for subnet in self.conn.network.subnets()
            if re.search("^192.168.", str(subnet["gateway_ip"]))
        )
        available_byte3 = list(str(x) for x in range(1, 255) if x not in currently_used)

        byte3 = random.choice(available_byte3)
        cidr = f"192.168.{byte3}.0/24"
        subnet_start = f"192.168.{byte3}.10"
        subnet_end = f"192.168.{byte3}.254"
        gateway_ip = f"192.168.{byte3}.1"

        # get network id
        network_id = self.find_resource_id(network, self.conn.network.find_network)
        if not network_id:
            return False, f"No Network Found with Name or ID {network}"

        try:
            subnet = self.conn.network.create_subnet(
                ip_version=4,
                network_id=network_id,
                allocation_pools=[{"start": subnet_start, "end": subnet_end}],
                cidr=cidr,
                gateway_ip=gateway_ip,
                **subnet_kwargs,
            )
        except ResourceNotFound as err:
            return False, f"Subnet Creation Failed {err}"
        return True, subnet
