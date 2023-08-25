import unittest


from enums.query.query_presets import QueryPresetsInteger

from openstack_query.handlers.client_side_handler_integer import (
    ClientSideHandlerInteger,
)
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access,


class ClientSideHandlerIntegerTests(unittest.TestCase):
    """
    Run various tests to ensure that ClientSideHandlerInteger class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        _filter_function_mappings = {
            preset: [MockProperties.PROP_1] for preset in QueryPresetsInteger
        }
        self.instance = ClientSideHandlerInteger(_filter_function_mappings)

    def test_check_supported_all_presets(self):
        """
        Tests that client_side_handler_integer supports all integer QueryPresets
        """
        self.assertTrue(
            self.instance.check_supported(preset, MockProperties.PROP_1)
            for preset in QueryPresetsInteger
        )

    def test_prop_less_than(self):
        """
        Tests that method prop_less_than functions expectedly
        Returns True if val1 is less than val2
        """
        for i, expected in (1, True), (2, False):
            assert self.instance._prop_less_than(i, 2) == expected

    def test_prop_greater_than(self):
        """
        Tests that method prop_greater_than functions expectedly
        Returns True if val1 is greater than val2
        """
        for i, expected in (1, False), (2, False), (3, True):
            assert self.instance._prop_greater_than(i, 2) == expected

    def test_prop_less_than_or_equal_to(self):
        """
        Tests that method prop_less_than_or_equal_to functions expectedly
        Returns True if val1 is less than or equal to val2
        """
        for i, expected in (1, True), (2, True), (3, False):
            assert self.instance._prop_less_than_or_equal_to(i, 2) == expected

    def test_prop_greater_than_or_equal_to(self):
        """
        Tests that method prop_greater_than_or_equal_to functions expectedly
        Returns True if val1 is greater than or equal to val2
        """
        for i, expected in (1, False), (2, True), (3, True):
            assert self.instance._prop_greater_than_or_equal_to(i, 2) == expected
