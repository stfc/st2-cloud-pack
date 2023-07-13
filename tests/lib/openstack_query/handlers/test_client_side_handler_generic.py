import unittest
from parameterized import parameterized

from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from enums.query.query_presets import QueryPresetsGeneric

from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


class ClientSideHandlerGenericTests(unittest.TestCase):
    """
    Run various tests to ensure that ClientSideHandlerGeneric class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        # sets filter function mappings so that PROP_1 is valid for all client_side
        _filter_function_mappings = {
            preset: [MockProperties.PROP_1] for preset in QueryPresetsGeneric
        }
        self.instance = ClientSideHandlerGeneric(_filter_function_mappings)

    @parameterized.expand(
        [(f"test {preset.name}", preset) for preset in QueryPresetsGeneric]
    )
    def test_check_supported_all_presets(self, _, preset):
        """
        Tests that client_side_handler_generic supports all generic QueryPresets
        """
        self.assertTrue(self.instance.check_supported(preset, MockProperties.PROP_1))

    @parameterized.expand(
        [
            ("test integer equal", 10, 10, True),
            ("test string equal", "some-string", "some-string", True),
            ("test integer not equal", 10, 8, False),
            ("test string not equal", "some-string", "some-other-string", False),
            ("test dict equal", {"a": 10}, {"a": 10}, True),
            ("test dict val not equal", {"a": 12}, {"a": 10}, False),
            ("test dict keys not equal", {"a": 12, "b": 12}, {"a": 12}, False),
        ]
    )
    def test_prop_equal_to(self, _, prop, value, expected_out):
        """
        Tests that method prop_equal_to functions expectedly
        Returns True if prop and value are equal
        """
        assert self.instance._prop_equal_to(prop, value) == expected_out

    @parameterized.expand(
        [
            ("test integer equal", 10, 10, False),
            ("test string equal", "some-string", "some-string", False),
            ("test integer not equal", 10, 8, True),
            ("test string not equal", "some-string", "some-other-string", True),
        ]
    )
    def test_prop_not_equal_to(self, _, prop, value, expected_out):
        """
        Tests that method not_prop_equal_to functions expectedly
        Returns True if prop and value are not equal
        """
        assert self.instance._prop_not_equal_to(prop, value) == expected_out
