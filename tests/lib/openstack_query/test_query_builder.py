import unittest
from unittest.mock import MagicMock, patch
from openstack_query.query_builder import QueryBuilder

from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

from exceptions.parse_query_error import ParseQueryError
from exceptions.query_preset_mapping_error import QueryPresetMappingError
from exceptions.query_property_mapping_error import QueryPropertyMappingError


class QueryBuilderTests(unittest.TestCase):
    """
    Runs various tests to ensure that QueryBuilder class methods function expectedly
    """

    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()
        self.mock_prop_handler = MagicMock()
        self.mock_preset_handlers = ["mock_preset_handler1", "mock_preset_handler2"]
        self.mock_kwarg_handler = MagicMock()
        self.instance = QueryBuilder(
            self.mock_prop_handler, self.mock_preset_handlers, self.mock_kwarg_handler
        )

    @patch("openstack_query.query_builder.QueryBuilder._get_preset_handler")
    def test_parse_where_valid(self, mock_get_preset_handler):
        """
        Tests that parse_where method sets up filter function and filter kwargs
        """

        mock_preset_handler = MagicMock()
        mock_preset_handler.get_filter_func.return_value = "some-filter-func"
        mock_get_preset_handler.return_value = mock_preset_handler

        self.mock_kwarg_handler.get_kwargs.return_value = "some-kwargs"
        self.mock_prop_handler.get_prop_mapping.return_value = "some-func"

        mock_kwargs = {"arg1": "val1", "arg2": "val2"}
        self.instance.parse_where(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_kwargs
        )

        mock_get_preset_handler.assert_called_once_with(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1
        )
        mock_preset_handler.get_filter_func.assert_called_once_with(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, "some-func", mock_kwargs
        )
        self.mock_kwarg_handler.get_kwargs.assert_called_once_with(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, "some-func", mock_kwargs
        )

        self.assertEqual(self.instance._filter_func, "some-filter-func")
        self.assertEqual(self.instance._filter_kwargs, "some-kwargs")

    def test_parse_where_invalid(self):
        # test if already set a query preset
        self.instance._filter_func = "previously-set-func"
        with self.assertRaises(ParseQueryError):
            self.instance.parse_where(MockQueryPresets.ITEM_1, MockProperties.PROP_1)

        # test if prop_mapping doesn't exist
        self.instance._filter_func = None
        self.mock_prop_handler.get_prop_mapping.return_value = None
        with self.assertRaises(QueryPropertyMappingError):
            self.instance.parse_where(MockQueryPresets.ITEM_1, MockProperties.PROP_1)

    def test_get_preset_handler(self):
        mock_preset1 = MagicMock()
        mock_preset1.check_supported.return_value = False

        mock_preset2 = MagicMock()
        mock_preset2.check_supported.return_value = True

        # check when preset found
        self.instance._preset_handlers = [mock_preset1, mock_preset2]
        res = self.instance._get_preset_handler(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1
        )
        self.assertEqual(res, mock_preset2)

        # check raises error when preset not found
        self.instance._preset_handlers = [mock_preset1]
        with self.assertRaises(QueryPresetMappingError):
            _ = self.instance._get_preset_handler(
                MockQueryPresets.ITEM_1, MockProperties.PROP_1
            )
