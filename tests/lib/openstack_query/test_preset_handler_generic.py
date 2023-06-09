import unittest
from unittest.mock import MagicMock, patch
from parameterized import parameterized

from nose.tools import raises

from openstack_query.preset_handlers.preset_handler_generic import PresetHandlerGeneric
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
        self.instance = PresetHandlerGeneric()

    @parameterized.expand(
        [(f"test {preset.name}", preset) for preset in QueryPresetsGeneric]
    )
    def test_check_preset_supported_all_presets(self, name, preset):
        """
        Tests that handler supports all generic query presets
        """
        self.assertTrue(self.instance.check_preset_supported(preset))

    @parameterized.expand(
        [(f"test {preset.name}", preset) for preset in QueryPresetsGeneric]
    )
    def test_get_mapping_all_presets(self, name, preset):
        """
        Tests that handler supports all generic query presets
        """
        self.assertIsNotNone(self.instance._get_mapping(preset))

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
