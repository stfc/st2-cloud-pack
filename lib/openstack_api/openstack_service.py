from typing import Dict
from openstack.connection import Connection
from openstack.compute.v2.service import Service
from openstack.compute.v2._proxy import Proxy 


def disable_service(
    conn: Connection,
    service: Service,
    hypervisor_name: str,
    service_binary:str,
    disabled_reason: str,
) -> None:
    """
    Disables an Openstack service
    :param conn: Openstack connection
    :param service: The instance of the service class.
    :param hypervisor_name (str): The name or ID of the hypervisor.
    :param service_binary: The name of the service.
    :param disabled_reason: The reason for disabling the service.
    """

    if service.status == "enabled":
        conn.compute.disable_service(service, host=hypervisor_name, binary=service_binary, disabled_reason=disabled_reason)
        print(f"The {service_binary} service has been disabled.")
    else:
        print("Hypervisor is currently disabled - aborting.")



def enable_service(
    conn: Connection, 
    service: Service,
    hypervisor_name: str,
    service_binary:str,
) -> None:
    """
    Enables an Openstack service
    :param conn: Openstack connection
    :param service: The instance of the service class.
    :param hypervisor_name (str): The name or ID of the hypervisor.
    :param service_binary: The name of the service.
    """
    
    if service.status == "disabled":
        conn.compute.enable_service(service, host=hypervisor_name, binary=service_binary)
        print(f"The {service_binary} service has been enabled.")
    else:
        print("Hypervisor is currently enabled - aborting.")