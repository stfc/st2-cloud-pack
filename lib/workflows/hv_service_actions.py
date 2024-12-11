from openstack.connection import Connection
from openstack_api.openstack_service import disable_service, enable_service


def hv_service_disable(
    conn: Connection,
    hypervisor_name: str,
    service_binary: str,
    disabled_reason: str,
) -> None:
    """
    Disables an Openstack service
    :param conn: Openstack connection
    :param hypervisor_name: The name or ID of the hypervisor.
    :param service_binary: The name of the service.
    :param disabled_reason: The reason for disabling the service.
    """

    service = conn.compute.find_service(
        service_binary, ignore_missing=False, host=hypervisor_name
    )

    disable_service(conn, service, hypervisor_name, service_binary, disabled_reason)


def hv_service_enable(
    conn: Connection,
    hypervisor_name: str,
    service_binary: str,
) -> None:
    """
    Enables an Openstack service
    :param conn: Openstack connection
    :param hypervisor_name: The name or ID of the hypervisor.
    :param service_binary: The name of the service.
    """

    service = conn.compute.find_service(
        service_binary, ignore_missing=False, host=hypervisor_name
    )

    enable_service(conn, service, hypervisor_name, service_binary)
