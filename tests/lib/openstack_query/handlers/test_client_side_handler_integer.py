import unittest
from parameterized import parameterized

from enums.query.query_presets import QueryPresetsInteger

from openstack_query.handlers.client_side_handler_integer import (
    ClientSideHandlerInteger,
)
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


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

    @parameterized.expand(
        [(f"test {preset.name}", preset) for preset in QueryPresetsInteger]
    )
    def test_check_supported_all_presets(self, name, preset):
        """
        Tests that client_side_handler_integer supports all integer QueryPresets
        """
        self.assertTrue(self.instance.check_supported(preset, MockProperties.PROP_1))

    @parameterized.expand(
        [
            ("test less than", 8, 10, True),
            ("test equal", 10, 10, False),
            ("test greater than", 10, 8, False),
        ]
    )
    def test_prop_less_than(self, name, val1, val2, expected_out):
        """
        Tests that method prop_less_than functions expectedly
        Returns True if val1 is less than val2
        """
        assert self.instance._prop_less_than(val1, val2) == expected_out

    @parameterized.expand(
        [
            ("test less than", 8, 10, False),
            ("test equal", 10, 10, False),
            ("test greater than", 10, 8, True),
        ]
    )
    def test_prop_greater_than(self, name, val1, val2, expected_out):
        """
        Tests that method prop_greater_than functions expectedly
        Returns True if val1 is greater than val2
        """
        assert self.instance._prop_greater_than(val1, val2) == expected_out

    @parameterized.expand(
        [
            ("test less than", 8, 10, True),
            ("test equal", 10, 10, True),
            ("test greater than", 10, 8, False),
        ]
    )
    def test_prop_less_than_or_equal_to(self, name, val1, val2, expected_out):
        """
        Tests that method prop_less_than_or_equal_to functions expectedly
        Returns True if val1 is less than or equal to val2
        """
        assert self.instance._prop_less_than_or_equal_to(val1, val2) == expected_out

    @parameterized.expand(
        [
            ("test less than", 8, 10, False),
            ("test equal", 10, 10, True),
            ("test greater than", 10, 8, True),
        ]
    )
    def test_prop_greater_than_or_equal_to(self, name, val1, val2, expected_out):
        """
        Tests that method prop_greater_than_or_equal_to functions expectedly
        Returns True if val1 is greater than or equal to val2
        """
        assert self.instance._prop_greater_than_or_equal_to(val1, val2) == expected_out
