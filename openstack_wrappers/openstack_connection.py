import openstack.connection
from openstack import connect


class OpenstackConnection:
    """
    Wraps an openstack connection as a context manager.
    This class is used as follows:
        with(OpenstackConnection()) as <name>:
            name.<openstack_API>.method()
    """

    def __init__(self, cloud_name: str):
        """
        Starts a connection with the Openstack API when used in a context manager
        :param cloud_name: The name of the cloud found in clouds.yaml
        """
        self._cloud_name = cloud_name
        self._connection = None

    def __enter__(self) -> openstack.connection.Connection:
        self._connection = connect(cloud=self._cloud_name)
        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()
        self._connection = None
