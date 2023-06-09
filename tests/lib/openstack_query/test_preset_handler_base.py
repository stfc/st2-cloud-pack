import unittest
from unittest.mock import MagicMock, patch
from parameterized import parameterized

from nose.tools import raises

from openstack_query.preset_handlers.preset_handler_base import PresetHandlerBase
from exceptions.query_preset_mapping_error import QueryPresetMappingError
from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets


class PresetHandlerBaseTests(unittest.TestCase):
    """
    Runs various tests to ensure that PresetHandlerBase class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        self.instance = PresetHandlerBase()
        self.instance._FILTER_FUNCTIONS = {
            MockQueryPresets.ITEM_1: "item1_func",
            MockQueryPresets.ITEM_2: "item2_func",
            MockQueryPresets.ITEM_3: "item3_func",
        }

    def test_check_preset_supported_true(self):
        self.assertTrue(self.instance.check_preset_supported(MockQueryPresets.ITEM_1))

    def test_check_preset_supported_false(self):
        self.assertFalse(self.instance.check_preset_supported(MockQueryPresets.ITEM_4))

    def test_get_mapping_valid(self):
        self.assertEqual(
            self.instance._get_mapping(MockQueryPresets.ITEM_1), "item1_func"
        )

    def test_get_mapping_invalid(self):
        self.assertIsNone(self.instance._get_mapping(MockQueryPresets.ITEM_4))

    @patch(
        "openstack_query.preset_handlers.preset_handler_base.PresetHandlerBase._get_mapping"
    )
    @patch(
        "openstack_query.preset_handlers.preset_handler_base.PresetHandlerBase._check_filter_func"
    )
    def test_get_filter_func_all_valid(self, mock_check_filter_func, mock_get_mapping):

        mock_prop_func = MagicMock()
        mock_prop_func.return_value = "prop_val"

        mock_kwargs = {"arg1": "val1", "arg2": "val2"}

        mock_filter_func = MagicMock()
        mock_filter_func.return_value = "some_val"

        mock_get_mapping.return_value = mock_filter_func
        mock_check_filter_func.return_value = True

        res = self.instance.get_filter_func(
            MockQueryPresets.ITEM_1, mock_prop_func, mock_kwargs
        )

        mock_get_mapping.assert_called_once_with(MockQueryPresets.ITEM_1)
        mock_check_filter_func.assert_called_once_with(
            MockQueryPresets.ITEM_1, mock_kwargs
        )

        res = res("openstack_resource")
        mock_prop_func.assert_called_once_with("openstack_resource")
        mock_filter_func.assert_called_once_with("prop_val", **mock_kwargs)
        self.assertEqual(res, "some_val")

    @raises(QueryPresetMappingError)
    @patch(
        "openstack_query.preset_handlers.preset_handler_base.PresetHandlerBase._get_mapping"
    )
    @patch(
        "openstack_query.preset_handlers.preset_handler_base.PresetHandlerBase._check_filter_func"
    )
    def test_get_filter_func_fail_check(self, mock_check_filter_func, mock_get_mapping):
        mock_prop_func = MagicMock()
        mock_prop_func.return_value = "prop_val"

        mock_kwargs = {"arg1": "val1", "arg2": "val2"}

        mock_filter_func = MagicMock()
        mock_filter_func.return_value = "some_val"

        mock_get_mapping.return_value = mock_filter_func
        mock_check_filter_func.side_effect = TypeError()
        self.instance.get_filter_func(
            MockQueryPresets.ITEM_1, mock_prop_func, mock_kwargs
        )

    @patch(
        "openstack_query.preset_handlers.preset_handler_base.PresetHandlerBase._get_mapping"
    )
    def test_get_filter_func_invalid_preset(self, mock_get_mapping):
        mock_prop_func = MagicMock()
        mock_prop_func.return_value = "prop_val"

        mock_kwargs = {"arg1": "val1", "arg2": "val2"}

        mock_get_mapping.return_value = None
        self.assertIsNone(
            self.instance.get_filter_func(
                MockQueryPresets.ITEM_1, mock_prop_func, mock_kwargs
            )
        )

    @parameterized.expand(
        [
            ("required args only", {"arg1": 12}),
            ("required and default", {"arg1": 12, "arg2": "non-default"}),
            ("required and kwarg", {"arg1": 12, "some_kwarg": "some-val"}),
            (
                "all possible",
                {"arg1": 12, "arg2": "non-default", "some_kwarg": "some-val"},
            ),
            (
                "different order",
                {"arg2": "non-default", "some_kwarg": "some-val", "arg1": 12},
            ),
        ]
    )
    def test_check_filter_func_valid(self, name, valid_kwargs_to_test):
        def mock_filter_func(prop, arg1: int, arg2: str = "some-default", **kwargs):
            return None

        self.assertTrue(
            self.instance._check_filter_func(
                mock_filter_func, func_kwargs=valid_kwargs_to_test
            )
        )
