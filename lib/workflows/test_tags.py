from openstack.connection import Connection


def test_tags(conn: Connection):
    print(dir(conn))
