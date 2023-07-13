import unittest

from parameterized import parameterized
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

    @parameterized.expand(
        [(f"test {prop.name.lower()}", prop) for prop in ServerProperties]
    )
    def test_get_prop_handler(self, _, prop):
        """
        Tests that all server properties have a property function mapping
        """
        prop_handler = self.instance._get_prop_handler()
        prop_handler.check_supported(prop)
