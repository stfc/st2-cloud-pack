from typing import Optional

from openstack.connection import Connection
from openstack_api.openstack_service import disable_service, enable_service


def hv_compute_service_disable(
    conn: Connection, 
    hypervisor_name: str,
    service_binary:str,
    disabled_reason: str,
) -> None:
    """
    Disables an Openstack service
    :param conn: Openstack connection
    :param service_identifier: The service ID or instance.
    :param hypervisor_name (str): The name or ID of the hypervisor.
    :param service_binary: The name of the service.
    :param disable_reason: The reason for disabling the service.
    """

    service = conn.compute.find_service(service_binary, ignore_missing=False, host=hypervisor_name)
    print(service)

    disable_service(conn, service, hypervisor_name, service_binary, disabled_reason)

    

def hv_compute_service_enable(
    conn: Connection, 
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

    service = conn.compute.find_service(service_binary, ignore_missing=False, host=hypervisor_name)

    enable_service(conn, service, hypervisor_name, service_binary)

