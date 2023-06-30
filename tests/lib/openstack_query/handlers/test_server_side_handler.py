import unittest
from unittest.mock import MagicMock, patch
from parameterized import parameterized

from openstack_query.handlers.server_side_handler import ServerSideHandler
from exceptions.query_preset_mapping_error import QueryPresetMappingError

from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


class ServerSideHandlerTests(unittest.TestCase):
    """
    Runs various tests to ensure that ServerSideHandler class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()

        _SERVER_SIDE_FUNCTION_MAPPINGS = {
            MockQueryPresets.ITEM_1: {
                MockProperties.PROP_1: "item1-prop1-kwarg",
                MockProperties.PROP_2: "item2-prop2-kwarg",
            },
            MockQueryPresets.ITEM_2: {
                MockProperties.PROP_3: "item2-prop3-kwarg",
                MockProperties.PROP_4: "item2-prop4-kwarg",
            },
        }
        self.instance = ServerSideHandler(_SERVER_SIDE_FUNCTION_MAPPINGS)

    def test_check_supported_true(self):
        self.assertTrue(
            self.instance.check_supported(
                MockQueryPresets.ITEM_1, MockProperties.PROP_1
            )
        )

    def test_check_supported_false(self):
        # when preset is not supported
        self.assertFalse(
            self.instance.check_supported(
                MockQueryPresets.ITEM_3, MockProperties.PROP_1
            )
        )

        # when preset found, but prop is not supported
        self.assertFalse(
            self.instance.check_supported(
                MockQueryPresets.ITEM_1, MockProperties.PROP_3
            )
        )

    def test_get_mapping_valid(self):
        self.assertEqual(
            self.instance._get_mapping(MockQueryPresets.ITEM_1, MockProperties.PROP_1),
            "item1-prop1-kwarg",
        )

    def test_get_mapping_invalid(self):
        # when preset is not supported
        self.assertIsNone(
            self.instance._get_mapping(MockQueryPresets.ITEM_3, MockProperties.PROP_1)
        )

        # when preset found, but prop is not supported
        self.assertIsNone(
            self.instance._get_mapping(MockQueryPresets.ITEM_1, MockProperties.PROP_3)
        )

    @patch(
        "openstack_query.handlers.server_side_handler.ServerSideHandler._check_filter_mapping"
    )
    @patch(
        "openstack_query.handlers.server_side_handler.ServerSideHandler._get_mapping"
    )
    def test_get_filters_valid(self, mock_get_mapping, mock_check_filter_mapping):
        mock_params = {"arg1": "val1", "arg2": "val2"}
        mock_filter_func = MagicMock()
        mock_filter_func.return_value = "a-kwarg-mapping"

        mock_check_filter_mapping.return_value = True, ""
        mock_get_mapping.return_value = mock_filter_func

        res = self.instance.get_filters(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_params
        )

        mock_check_filter_mapping.assert_called_once_with(mock_filter_func, mock_params)
        mock_filter_func.assert_called_once_with(**mock_params)
        self.assertEqual(res, "a-kwarg-mapping")

    @patch(
        "openstack_query.handlers.server_side_handler.ServerSideHandler._check_filter_mapping"
    )
    def test_get_filters_invalid(self, mock_check_filter_mapping):
        mock_params = {"arg1": "val1", "arg2": "val2"}
        mock_kwarg_func = MagicMock()

        # when preset/prop not supported
        res = self.instance.get_filters(
            MockQueryPresets.ITEM_3, MockProperties.PROP_1, mock_params
        )
        self.assertIsNone(res)

        # when preset/prop are supported, but wrong kwarg_params
        mock_check_filter_mapping.return_value = False, "some-reason"
        with self.assertRaises(QueryPresetMappingError):
            self.instance.get_filters(
                MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_params
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
    def test_check_filter_mapping(self, name, valid_params_to_test):
        mock_server_side_mapping = lambda arg1, arg2="some-default", **kwargs: {
            "kwarg1": "val1"
        }
        self.assertTrue(
            self.instance._check_filter_mapping(
                mock_server_side_mapping, filter_params=valid_params_to_test
            )
        )