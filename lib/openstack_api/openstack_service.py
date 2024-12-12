from typing import Optional
from openstack.connection import Connection
from openstack.compute.v2.service import Service


def disable_service(
    conn: Connection,
    service: Service,
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

    if service.status == "enabled":
        return conn.compute.disable_service(
            service,
            host=hypervisor_name,
            binary=service_binary,
            disabled_reason=disabled_reason,
        )
    raise RuntimeError(
        f"Failed to disable {service_binary} on {hypervisor_name}. Already disabled."
    )


def enable_service(
    conn: Connection,
    service: Service,
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

    if service.status == "disabled":
        return conn.compute.enable_service(
            service, host=hypervisor_name, binary=service_binary
        )
    raise RuntimeError(
        f"Failed to enable {service_binary} on {hypervisor_name}. Already enabled."
    )
