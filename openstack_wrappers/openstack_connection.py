import openstack.connection
from openstack import connect


class OpenstackConnection:
    def __init__(self):
        self._connection = None

    def __enter__(self) -> openstack.connection.Connection:
        if not self._connection:
            # TODO params
            self._connection = connect()
        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()
        self._connection = None
