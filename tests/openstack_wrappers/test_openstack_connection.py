from unittest import mock

from openstack_wrappers.openstack_connection import OpenstackConnection


def test_openstack_connection_connects_first_time():
    """
    Tests that connect it correctly called on entry.
    Does not check the args passed to connect
    """
    with mock.patch(
        "openstack_wrappers.openstack_connection.connect"
    ) as patched_connect:
        with OpenstackConnection("") as instance:
            patched_connect.assert_called_once()
            assert instance == patched_connect.return_value


def test_openstack_connection_uses_cloud_name():
    expected_cloud = "foo"
    with mock.patch(
        "openstack_wrappers.openstack_connection.connect"
    ) as patched_connect:
        with OpenstackConnection(expected_cloud):
            patched_connect.assert_called_once_with(cloud=expected_cloud)


def test_openstack_connection_disconnects():
    """
    Checks the session is correctly closed (to not leak handles)
    when the context manager exits
    """
    with mock.patch(
        "openstack_wrappers.openstack_connection.connect"
    ) as patched_connect:
        with OpenstackConnection("") as instance:
            connection_handle = patched_connect.return_value
            assert instance == connection_handle
        connection_handle.close.assert_called_once()


def test_openstack_connection_connects_second_time():
    """
    Tests that creating two connections calls connect twice.
    Why, because Singletons are evil and cause nothing but problems
    """
    with mock.patch(
        "openstack_wrappers.openstack_connection.connect"
    ) as patched_connect:
        with OpenstackConnection(""):
            pass
        with OpenstackConnection(""):
            assert patched_connect.call_count == 2
