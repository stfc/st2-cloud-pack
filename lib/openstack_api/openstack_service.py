from typing import Dict
from openstack.connection import Connection
from openstack.compute.v2.service import Service
from openstack.compute.v2._proxy import Proxy

'''
Find hypervisor, using user input // Hypervisor not found
Check to see if Nova-Compute service exists using the service ID
If it does, check if it's already enbabled/disabled
Enable/disable the service
Let user know that's the action is complete (print output)


Side effects:
Authenticate the connection (already done)
Api call to endpoint to find service (hypervisor not found, service not found)
Authentication failed to hypervisor and/or service (handled by )
Networking issues, talking to openstack api, too slow, no response (ahndled by openstack api)
'''    


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
    :param service_identifier: The service ID or instance.
    :param hypervisor_name (str): The name or ID of the hypervisor.
    :param service_binary: The name of the service.
    :param disable_reason: The reason for disabling the service.
    """

    print(service)
    if service.status == "enabled":
        conn.compute.disable_service(service, host=hypervisor_name, binary=service_binary, disabled_reason=disabled_reason)
        print("Disabled the status")
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
    :param service_identifier: The service ID or instance.
    :param hypervisor_name (str): The name or ID of the hypervisor.
    :param service_binary: The name of the service.
    """
    
    if service.status == "disabled":
        conn.compute.enable_service(service, host=hypervisor_name, binary=service_binary)
        print(f"The {service_binary} service has been enabled.")
    else:
        print("Hypervisor is currently enabled - aborting.")