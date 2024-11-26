from typing import Optional

from openstack.connection import Connection
from openstack_api.openstack_service import disable_service, enable_service
#from openstack_api.openstack_hypervisor import get_hypervisor_state


def hv_compute_service_disable(
    conn: Connection, 
    service_identifier: str,
    hypervisor_name: str,
    service_binary:str,
    disable_reason: str,
) -> None:
    """
    Disables an Openstack service
    :param conn: Openstack connection
    :param service_identifier: The service ID or instance.
    :param hypervisor_name (str): The name or ID of the hypervisor.
    :param service_binary: The name of the service.
    :param disable_reason: The reason for disabling the service.
    """

    service = conn.compute.find_service("nova-compute", host=hypervisor_name)
    service_binary = "nova-compute"

    if service:
            disable_service(conn, service_identifier, hypervisor_name, service_binary, disable_reason)
    else:
        return "No Nova-Compute services found."
    

def hv_compute_service_enable(
    conn: Connection, 
    service_identifier: str,
    hypervisor_name: str,
    service_binary:str,
) -> None:
    """
    Enables an Openstack service
    :param conn: Openstack connection
    :param service_identifier: The service ID or instance.
    :param hypervisor_name (str): The name or ID of the hypervisor.
    :param service_binary: The name of the service.
    """

    service = conn.compute.find_service("nova-compute", host=hypervisor_name)
    service_binary = "nova-compute"

    if service:
            enable_service(conn, service_identifier, hypervisor_name, service_binary)
    else:
        return "No Nova-Compute services found."
