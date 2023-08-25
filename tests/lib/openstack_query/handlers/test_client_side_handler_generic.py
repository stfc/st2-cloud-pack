import unittest


from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from enums.query.query_presets import QueryPresetsGeneric

from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


TEST_CORPUS = [1, "foo", None, {"a": "b"}]


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

    def test_check_supported_all_presets(self):
        """
        Tests that client_side_handler_generic supports all generic QueryPresets
        """
        self.assertTrue(self.instance.check_supported(preset, MockProperties.PROP_1) for preset in QueryPresetsGeneric)

    def test_prop_equal_to_valid(self):
        """
        Tests that method prop_equal_to functions expectedly
        """
        for i in TEST_CORPUS:
            assert self.instance._prop_equal_to(i, i)

    def test_prop_equal_to_invalid(self):
        """
        Tests that method prop_equal_to functions expectedly
        """
        for i in TEST_CORPUS:
            assert not self.instance._prop_equal_to(i, "not equal")

    def test_prop_not_equal_to_valid(self):
        """
        Tests that method not_prop_equal_to functions expectedly
        """
        for i in TEST_CORPUS:
            assert self.instance._prop_not_equal_to(i, "FOO")

    def test_prop_not_equal_to_invalid(self):
        """
        Tests that method not_prop_equal_to functions expectedly
        """
        for i in TEST_CORPUS:
            assert not self.instance._prop_not_equal_to(i, i)
