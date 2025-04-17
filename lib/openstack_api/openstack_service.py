from typing import Optional
from openstack.connection import Connection
from openstack.compute.v2.service import Service


def disable_service(
    conn: Connection,
    hypervisor_name: str,
    service_binary: str,
    disabled_reason: str,
) -> Optional[Service]:
    """
    Disables an Openstack service
    :param conn: Openstack connection
    :param service: The instance of the service class.
    :param hypervisor_name: The name or ID of the hypervisor.
    :param service_binary: The name of the service.
    :param disabled_reason: The reason for disabling the service.
    :return: Returns the Service object.
    """
    service = conn.compute.find_service(
        service_binary, ignore_missing=False, host=hypervisor_name
    )
    # Needs to be service.id since just passing service won't update the service correctly
    return conn.compute.disable_service(
        service=service.id,
        disabled_reason=disabled_reason,
    )


def enable_service(
    conn: Connection,
    hypervisor_name: str,
    service_binary: str,
) -> Optional[Service]:
    """
    Enables an Openstack service
    :param conn: Openstack connection
    :param service: The instance of the service class.
    :param hypervisor_name: The name or ID of the hypervisor.
    :param service_binary: The name of the service.
    :return: Returns the Service object.
    """
    service = conn.compute.find_service(
        service_binary, ignore_missing=False, host=hypervisor_name
    )
    return conn.compute.enable_service(service=service.id)
