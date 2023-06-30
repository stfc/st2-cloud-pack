import unittest
from unittest.mock import MagicMock, patch
from parameterized import parameterized

from openstack_query.handlers.client_side_handler import ClientSideHandler
from exceptions.query_preset_mapping_error import QueryPresetMappingError

from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


class ClientSideHandlerBaseTests(unittest.TestCase):
    """
    Runs various tests to ensure that ClientSideHandlerBase class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()

        _FILTER_FUNCTION_MAPPINGS = {
            MockQueryPresets.ITEM_1: ["*"],
            MockQueryPresets.ITEM_2: [MockProperties.PROP_1, MockProperties.PROP_2],
            MockQueryPresets.ITEM_3: [MockProperties.PROP_3, MockProperties.PROP_4],
        }
        self.instance = ClientSideHandler(_FILTER_FUNCTION_MAPPINGS)
        self.instance._FILTER_FUNCTIONS = {
            MockQueryPresets.ITEM_1: "item1_func",
            MockQueryPresets.ITEM_2: "item2_func",
            MockQueryPresets.ITEM_3: "item3_func",
        }

    def test_check_supported_true(self):
        # when preset has '*' mapping - accepts all props
        self.assertTrue(
            self.instance.check_supported(
                MockQueryPresets.ITEM_1, MockProperties.PROP_1
            )
        )

        # when preset has explicit prop mapping
        self.assertTrue(
            self.instance.check_supported(
                MockQueryPresets.ITEM_2, MockProperties.PROP_2
            )
        )

    def test_check_preset_supported_false(self):
        # when preset is not supported
        self.assertFalse(
            self.instance.check_supported(
                MockQueryPresets.ITEM_4, MockProperties.PROP_1
            )
        )

        # when preset found, but prop is not supported
        self.assertFalse(
            self.instance.check_supported(
                MockQueryPresets.ITEM_2, MockProperties.PROP_3
            )
        )

    @patch(
        "openstack_query.handlers.client_side_handler.ClientSideHandler._check_filter_func"
    )
    @patch(
        "openstack_query.handlers.client_side_handler.ClientSideHandler._filter_func_wrapper"
    )
    def test_get_filter_func_valid(
        self, mock_filter_func_wrapper, mock_check_filter_func
    ):
        # define inputs
        mock_prop_func = MagicMock()
        mock_kwargs = {"arg1": "val1", "arg2": "val2"}

        # mock function return values
        mock_check_filter_func.return_value = True, ""
        mock_filter_func_wrapper.return_value = "a-boolean-value"

        res = self.instance.get_filter_func(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_prop_func, mock_kwargs
        )
        val = res("test-openstack-res")

        # MockQueryPresets.ITEM_1 and MockProperties.PROP_1 are valid and should return 'item1_func'
        # - which represents a function mapping
        mock_check_filter_func.assert_called_once_with("item1_func", mock_kwargs)
        mock_filter_func_wrapper.assert_called_once_with(
            "test-openstack-res", "item1_func", mock_prop_func, mock_kwargs
        )

        self.assertEqual(val, "a-boolean-value")

    @patch(
        "openstack_query.handlers.client_side_handler.ClientSideHandler._check_filter_func"
    )
    def test_get_filter_func_invalid(self, mock_check_filter_func):
        mock_prop_func = MagicMock()
        mock_kwargs = {"arg1": "val1", "arg2": "val2"}

        # when preset is invalid
        with self.assertRaises(QueryPresetMappingError):
            self.instance.get_filter_func(
                MockQueryPresets.ITEM_4,
                MockProperties.PROP_1,
                mock_prop_func,
                mock_kwargs,
            )

        # when the preset is valid, but property is invalid
        with self.assertRaises(QueryPresetMappingError):
            self.instance.get_filter_func(
                MockQueryPresets.ITEM_2,
                MockProperties.PROP_3,
                mock_prop_func,
                mock_kwargs,
            )

        # when check_filter_func is false
        mock_check_filter_func.return_value = False, "some-error"
        with self.assertRaises(QueryPresetMappingError):
            self.instance.get_filter_func(
                MockQueryPresets.ITEM_1,
                MockProperties.PROP_1,
                mock_prop_func,
                mock_kwargs,
            )

    def test_filter_func_wrapper(self):
        mock_item = "some-openstack-item"
        mock_filter_func = MagicMock()
        mock_prop_func = MagicMock()
        mock_filter_func_kwargs = {"arg1": "val1", "arg2": "val2"}
        mock_filter_func.return_value = "a-boolean-value"

        # when prop_func raises exception - i.e. property not found
        mock_prop_func.side_effect = AttributeError()
        res = self.instance._filter_func_wrapper(
            mock_item, mock_filter_func, mock_prop_func, mock_filter_func_kwargs
        )
        self.assertFalse(res)

        # when prop_func is valid and filter_kwargs given
        mock_prop_func.return_value = "some-prop-val"
        mock_prop_func.side_effect = None
        res = self.instance._filter_func_wrapper(
            mock_item, mock_filter_func, mock_prop_func, mock_filter_func_kwargs
        )
        self.assertEqual(res, "a-boolean-value")
        mock_filter_func.assert_called_once_with(
            "some-prop-val", **mock_filter_func_kwargs
        )

        # when prop_func is valid and filter_kwargs not given
        mock_prop_func.reset_mock()
        mock_filter_func.reset_mock()
        mock_prop_func.return_value = "some-prop-val"
        mock_prop_func.side_effect = None
        res = self.instance._filter_func_wrapper(
            mock_item, mock_filter_func, mock_prop_func
        )
        self.assertEqual(res, "a-boolean-value")
        mock_filter_func.assert_called_once_with("some-prop-val")

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
    def test_check_filter_func(self, name, valid_kwargs_to_test):
        def mock_filter_func(prop, arg1: int, arg2: str = "some-default", **kwargs):
            return None

        self.assertTrue(
            self.instance._check_filter_func(
                mock_filter_func, func_kwargs=valid_kwargs_to_test
            )
        )

    @parameterized.expand(
        [
            ("no required", {}),
            ("required wrong type", {"arg1": "non-default"}),
            ("optional wrong type", {"arg1": 12, "arg2": 12}),
        ]
    )
    def test_check_filter_func(self, name, invalid_kwargs_to_test):
        def mock_filter_func(prop, arg1: int, arg2: str = "some-default", **kwargs):
            return None

        self.assertFalse(
            self.instance._check_filter_func(
                mock_filter_func, func_kwargs=invalid_kwargs_to_test
            )[0]
        )
