import unittest


from openstack_query.queries.server_query import ServerQuery
from enums.query.props.server_properties import ServerProperties

# pylint:disable=protected-access


class TestServerQuery(unittest.TestCase):
    """
    Runs various tests to ensure that ServerQuery functions expectedly.
    """

    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()
        self.instance = ServerQuery()

    def test_get_prop_handler(self):
        """
        Tests that all server properties have a property function mapping
        """
        prop_handler = self.instance._get_prop_handler()
        for prop in ServerProperties:
            prop_handler.check_supported(prop)
