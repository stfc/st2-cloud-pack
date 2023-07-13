import unittest
from unittest.mock import MagicMock, patch, NonCallableMock
from parameterized import parameterized

from openstack_query.handlers.client_side_handler import ClientSideHandler
from exceptions.query_preset_mapping_error import QueryPresetMappingError

from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


class ClientSideHandlerBaseTests(unittest.TestCase):
    """
    Runs various tests to ensure that ClientSideHandlerBase class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()

        _filter_function_mappings = {
            MockQueryPresets.ITEM_1: ["*"],
            MockQueryPresets.ITEM_2: [MockProperties.PROP_1, MockProperties.PROP_2],
            MockQueryPresets.ITEM_3: [MockProperties.PROP_3, MockProperties.PROP_4],
        }
        self.instance = ClientSideHandler(_filter_function_mappings)
        self.instance._filter_functions = {
            MockQueryPresets.ITEM_1: "item1_func",
            MockQueryPresets.ITEM_2: "item2_func",
            MockQueryPresets.ITEM_3: "item3_func",
        }

    def test_check_supported_true(self):
        """
        Tests that check_supported method works expectedly
        returns True if Prop Enum and Preset Enum have client-side mapping
        """
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
        """
        Tests that check_supported method works expectedly
        returns False if either Preset is not supported or Preset-Prop does not have a mapping
        """

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
        """
        Tests that get_filter_func method works expectedly - with valid inputs
        sets up and returns a function that when given an openstack object will return a boolean value on
        whether it passes the filter
        """
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

    def test_get_filter_func_preset_invalid(self):
        """
        Tests that get_filter_func method works expectedly - with invalid inputs
        raises QueryPresetMappingError if preset invalid
        """
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

    def test_get_filter_func_prop_invalid(self):
        """
        Tests that get_filter_func method works expectedly - with invalid inputs
        raises QueryPresetMappingError if prop invalid
        """

        # when the preset is valid, but property is invalid
        with self.assertRaises(QueryPresetMappingError):
            mock_prop_func = MagicMock()
            mock_kwargs = {"arg1": "val1", "arg2": "val2"}
            self.instance.get_filter_func(
                MockQueryPresets.ITEM_2,
                MockProperties.PROP_3,
                mock_prop_func,
                mock_kwargs,
            )

    @patch(
        "openstack_query.handlers.client_side_handler.ClientSideHandler._check_filter_func"
    )
    def test_get_filter_func_arguments_invalid(self, mock_check_filter_func):
        """
        Tests that get_filter_func method works expectedly - with invalid inputs
        raises QueryPresetMappingError if filter_func_kwargs are invalid
        """
        mock_prop_func = MagicMock()
        mock_kwargs = {"arg1": "val1", "arg2": "val2"}
        # when check_filter_func is false
        mock_check_filter_func.return_value = False, "some-error"
        with self.assertRaises(QueryPresetMappingError):
            self.instance.get_filter_func(
                MockQueryPresets.ITEM_1,
                MockProperties.PROP_1,
                mock_prop_func,
                mock_kwargs,
            )

    def test_filter_func_wrapper_prop_func_error(self):
        """
        Tests that get_filter_func method works expectedly - with invalid inputs
        raises QueryPresetMappingError if filter_func_kwargs are invalid
        """
        mock_item = NonCallableMock()

        mock_filter_func = MagicMock()
        mock_filter_func.return_value = "a-boolean-value"

        mock_prop_func = MagicMock()
        mock_filter_func_kwargs = {"arg1": "val1", "arg2": "val2"}

        # when prop_func raises exception - i.e. property not found
        mock_prop_func.side_effect = AttributeError()
        res = self.instance._filter_func_wrapper(
            mock_item, mock_filter_func, mock_prop_func, mock_filter_func_kwargs
        )
        self.assertFalse(res)

    def test_filter_func_wrapper_valid(self):
        """
        Tests that filter_func_wrapper method works expectedly - with valid inputs
        returns a function that takes an openstack item as input and returns either True or False
        on whether that item passes the set filter condition.
            - Prop Enum and Preset Enum are supported
            - and filter_func_kwargs are valid
        """
        mock_item = NonCallableMock()

        mock_filter_func = MagicMock()
        mock_filter_func.return_value = "a-boolean-value"

        mock_prop_func = MagicMock()
        mock_filter_func_kwargs = {"arg1": "val1", "arg2": "val2"}

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
            ("required args only", {"arg1": 12}, True),
            ("required and default", {"arg1": 12, "arg2": "non-default"}, True),
            ("required and kwarg", {"arg1": 12, "some_kwarg": "some-val"}, True),
            (
                "all possible",
                {"arg1": 12, "arg2": "non-default", "some_kwarg": "some-val"},
                True,
            ),
            (
                "different order",
                {"arg2": "non-default", "some_kwarg": "some-val", "arg1": 12},
                True,
            ),
            ("no required", {}, False),
            ("required wrong type", {"arg1": "non-default"}, False),
            ("optional wrong type", {"arg1": 12, "arg2": 12}, False),
        ]
    )
    def test_check_filter_func(self, _, kwargs_to_test, expected_value):
        """
        Tests that check_filter_func method works expectedly - for filter_func which takes extra params
        returns True only if args match expected args required by client-side filter function
        """

        # pylint:disable=unused-argument
        def mock_filter_func(prop, arg1: int, arg2: str = "some-default", **kwargs):
            return None

        res = self.instance._check_filter_func(
            mock_filter_func, func_kwargs=kwargs_to_test
        )
        self.assertEqual(expected_value, res[0])

    @parameterized.expand(
        [
            ("empty", {}, True),
            ("provided invalid arg", {"arg1": "non-default"}, False),
        ]
    )
    def test_check_filter_func_with_no_args(self, _, kwargs_to_test, expected_value):
        """
        Tests that check_filter_func method works expectedly - for filter_func which takes no extra params
        returns True if args match expected args required by client-side filter function
        """

        # pylint:disable=unused-argument
        def mock_filter_func(prop):
            return None

        res = self.instance._check_filter_func(
            mock_filter_func, func_kwargs=kwargs_to_test
        )
        self.assertEqual(expected_value, res[0])
