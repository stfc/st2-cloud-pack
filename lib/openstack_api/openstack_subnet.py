import ipaddress
import random
from typing import List

from openstack.connection import Connection
from openstack.network.v2.subnet import Subnet

from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError


def create_subnet(
    conn: Connection,
    network_identifier: str,
    subnet_name: str,
    subnet_description: str,
    dhcp_enabled: bool,
) -> Subnet:
    """
    Adds a new subnet with a randomly selected 192.168.x.0/24 to a given network
    :param conn: openstack connection object
    :param network_identifier: The network to add the new subnet to
    :param subnet_name: The new subnet name
    :param subnet_description: The new subnet description
    :param dhcp_enabled: Whether to enable DHCP on the new subnet
    :return: The newly created subnet object
    """
    network_identifier = network_identifier.strip()
    if not network_identifier:
        raise MissingMandatoryParamError("A network name or ID is required")
    network = conn.network.find_network(network_identifier, ignore_missing=False)

    subnet_name = subnet_name.strip()
    if not subnet_name:
        raise MissingMandatoryParamError("A new subnet name is required")

    selected_subnet = _select_random_subnet(conn, network.id)
    hosts = [str(i) for i in selected_subnet.hosts()]
    # Check our first entry is the gateway
    assert hosts[0].endswith(".1")

    return conn.network.create_subnet(
        ip_version=4,
        network_id=network.id,
        # Reserve the first 10 addresses from DHCP allocation
        allocation_pools=[{"start": hosts[10], "end": hosts[-1]}],
        cidr=str(selected_subnet),
        gateway_ip=hosts[0],
        name=subnet_name,
        description=subnet_description,
        is_dhcp_enabled=dhcp_enabled,
    )


def _select_random_subnet(conn: Connection, network_id) -> ipaddress.IPv4Network:
    """
    Selects a random subnet from the given network that isn't used
    :param conn: openstack connection object
    :param network_id: The network id to search
    :return: A randomly selected subnet
    """
    avail = [ipaddress.ip_network(f"192.168.{i}.0/24") for i in range(1, 255)]

    used_subnets = _find_used_subnet_nets(conn, network_id)
    avail = [i for i in avail if i not in used_subnets]
    if not avail:
        raise ItemNotFoundError("No available subnets")
    return random.choice(avail)


def _find_used_subnet_nets(
    conn: Connection, network_id: str
) -> List[ipaddress.IPv4Network]:
    """
    Gets the subnets associated with a given network
    :param conn: openstack connection object
    :param network_id: The network id to search
    :return: A list of found network addresses
    """
    subnets = [
        subnet.gateway_ip for subnet in conn.network.subnets(network_id=network_id)
    ]

    # Force to a /24 network
    return [ipaddress.ip_network(i + "/24", strict=False) for i in subnets]
