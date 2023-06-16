import unittest
from unittest.mock import MagicMock, patch
from parameterized import parameterized

from nose.tools import raises

from openstack_query.handlers.presets.preset_handler_generic import PresetHandlerGeneric
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

from enums.query.query_presets import QueryPresetsGeneric


class PresetHandlerGenericTests(unittest.TestCase):
    """
    Run various tests to ensure that PresetHandlerGeneric class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        # sets filter function mappings so that PROP_1 is valid for all presets
        _FILTER_FUNCTION_MAPPINGS = {
            preset: [MockProperties.PROP_1] for preset in QueryPresetsGeneric
        }
        self.instance = PresetHandlerGeneric(_FILTER_FUNCTION_MAPPINGS)

    @parameterized.expand(
        [(f"test {preset.name}", preset) for preset in QueryPresetsGeneric]
    )
    def test_check_supported_all_presets(self, name, preset):
        """
        Tests that handler supports all generic query presets
        """
        self.assertTrue(self.instance.check_supported(preset, MockProperties.PROP_1))

    @parameterized.expand(
        [(f"test {preset.name}", preset) for preset in QueryPresetsGeneric]
    )
    def test_get_mapping_all_presets(self, name, preset):
        """
        Tests that handler supports all generic query presets
        """
        self.assertIsNotNone(self.instance._get_mapping(preset, MockProperties.PROP_1))

    @parameterized.expand(
        [
            ("test integer equal", 10, 10, True),
            ("test string equal", "some-string", "some-string", True),
            ("test integer not equal", 10, 8, False),
            ("test string not equal", "some-string", "some-other-string", False),
        ]
    )
    def test_prop_equal_to(self, name, prop, value, expected_out):
        assert self.instance._prop_equal_to(prop, value) == expected_out

    @parameterized.expand(
        [
            ("test integer equal", 10, 10, False),
            ("test string equal", "some-string", "some-string", False),
            ("test integer not equal", 10, 8, True),
            ("test string not equal", "some-string", "some-other-string", True),
        ]
    )
    def test_prop_not_equal_to(self, name, prop, value, expected_out):
        assert self.instance._prop_not_equal_to(prop, value) == expected_out
