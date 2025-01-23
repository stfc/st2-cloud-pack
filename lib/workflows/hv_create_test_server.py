import random
from openstack.connection import Connection
from openstack_api.openstack_server import build_server, delete_server
from openstack_api.openstack_hypervisor import get_avaliable_flavors


def create_test_server(conn: Connection, hypervisor_name: str, test_all_flavors: bool):
    flavors = get_avaliable_flavors(conn, hypervisor_name)
    images = conn.image.images(status="active")

    if test_all_flavors:
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
    server = build_server(
        conn,
        "stackstorm-test-server",
        random.choice(flavors),
        "ubuntu-focal-20.04-nogui",
        "Internal",
        hypervisor_name,
    )
    delete_server(conn, server.id)
