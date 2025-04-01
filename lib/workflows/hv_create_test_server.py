import random

from openstack.connection import Connection
from openstack_api.openstack_hypervisor import get_available_flavors
from openstack_api.openstack_server import build_server, delete_server


def create_test_server(
    conn: Connection,
    hypervisor_name: str,
    test_all_flavors: bool,
    delete_on_failure: bool,
) -> None:
    """
    Create a test server on a hypervisor, option to test all possible flavors avaliable to the hypervisor

    :param conn: openstack connection object
    :type conn: Connection
    :param hypervisor_name: Hostname of the hypervisor
    :type hypervisor_name: str
    :param test_all_flavors: Option to test all possible flavors avaliable to the hypervisor
    :type test_all_flavors: bool
    :return: None
    :rtype: None
    """
    flavors = get_available_flavors(conn, hypervisor_name)

    if not test_all_flavors:
        flavors = [random.choice(flavors)]
    for flavor in flavors:
        server = build_server(
            conn,
            "stackstorm-test-server",
            flavor,
            "ubuntu-jammy-22.04-nogui",
            "Internal",
            hypervisor_name,
            delete_on_failure,
        )
        delete_server(conn, server.id)
