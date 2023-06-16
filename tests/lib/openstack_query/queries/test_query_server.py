import unittest
from unittest.mock import MagicMock, patch

from parameterized import parameterized
from openstack_query.queries.query_server import QueryServer
from enums.query.server_properties import ServerProperties


class TestQueryServer(unittest.TestCase):
    """
    Runs various tests to ensure that QueryServer functions expectedly.
    """

    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()
        self.instance = QueryServer()

    @parameterized.expand(
        [(f"test {prop.name.lower()}", prop) for prop in ServerProperties]
    )
    def test_all_properties_have_func_mapping(self, name, prop):
        """
        Tests that all openstack properties have a property function mapping
        """
        assert self.instance.builder._prop_handler.check_supported(prop)
