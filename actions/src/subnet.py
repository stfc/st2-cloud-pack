from st2common.runners.base_action import Action
import openstack
import random
import re
from openstack_action import OpenstackAction
import json

class Subnet(OpenstackAction):

    def __init__(self, *args, **kwargs):
        """ constructor class """
        super().__init__(*args, **kwargs)

        # lists possible functions that could be run as an action
        self.func = {
            "subnet_create": self.subnet_create
        }

    def subnet_create(self, **kwargs):
        """
        Create a Subnet on a Network
        :param kwargs: network (String): ID or Name, (other_args - see action definintion yaml file for details)
        :return: (status (Bool), reason/output (String/Dict))
        """
        new_kwargs = {k:v for k, v in kwargs.items() if k not in ["network"]}

        # calculate and choose random available gateway ip
        currently_used=[subnet["gateway_ip"].split(".")[2] for subnet in self.conn.network.subnets() if re.search("^192.168.", str(subnet["gateway_ip"]))]
        available_byte3 = list(set([str(x) for x in range(1, 255)]) - set(currently_used))

        byte3 = random.choice(available_byte3)
        cidr = "192.168.{}.0/24".format(byte3)
        subnet_start = "192.168.{}.10".format(byte3)
        subnet_end = "192.168.{}.254".format(byte3)
        gateway_ip = "192.168.{}.1".format(byte3)

        #get network id
        network_id = self.find_resource_id(kwargs["network"], self.conn.network.find_network)
        if not network_id:
            return False, "No Network Found with Name or ID {}".format(kwargs["network"])

        try:
            subnet = self.conn.network.create_subnet(ip_version=4, network_id=network_id, allocation_pools=[{"start":subnet_start,"end":subnet_end}], cidr=cidr, gateway_ip=gateway_ip, **new_kwargs)
        except Exception as e:
            return False, "Subnet Creation Failed {}".format(e)
        return True, subnet
