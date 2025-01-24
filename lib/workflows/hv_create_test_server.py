import random

from openstack.connection import Connection
from openstack_api.openstack_hypervisor import get_available_flavors
from openstack_api.openstack_server import build_server, delete_server


def create_test_server(conn: Connection, hypervisor_name: str, test_all_flavors: bool):
    flavors = get_available_flavors(conn, hypervisor_name)

    if not test_all_flavors:
        flavors = [random.choice(flavors)]
    for flavor in flavors:
        server = build_server(
            conn,
            "stackstorm-test-server",
            flavor,
            "ubuntu-focal-20.04-nogui",
            "Internal",
            hypervisor_name,
        )
        delete_server(conn, server.id)
