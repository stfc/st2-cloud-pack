import unittest
from unittest.mock import MagicMock, patch, NonCallableMock
from openstack_query.query_builder import QueryBuilder

from nose.tools import raises

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

        self.mock_client_handler_1 = MagicMock()
        self.mock_client_handler_2 = MagicMock()

        self.mock_client_side_handlers = [
            self.mock_client_handler_1,
            self.mock_client_handler_2,
        ]
        self.mock_server_side_handler = MagicMock()
        self.instance = QueryBuilder(
            self.mock_prop_handler,
            self.mock_client_side_handlers,
            self.mock_server_side_handler,
        )

    @patch("openstack_query.query_builder.QueryBuilder._get_preset_handler")
    def test_parse_where_valid(self, mock_get_preset_handler):
        """
        Tests that parse_where functions expectedly - where inputs valid
        method finds and sets client_side_filter and server_side_filters internal attributes
        """

        # setup mocks
        mock_client_side_handler = MagicMock()
        mock_get_preset_handler.return_value = mock_client_side_handler

        mock_client_filter_func = MagicMock()
        mock_client_side_handler.get_filter_func.return_value = mock_client_filter_func

        mock_server_filters = NonCallableMock()
        self.mock_server_side_handler.get_filters.return_value = mock_server_filters

        mock_prop_func = MagicMock()
        self.mock_prop_handler.get_prop_mapping.return_value = mock_prop_func

        mock_kwargs = {"arg1": "val1", "arg2": "val2"}
        self.instance.parse_where(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_kwargs
        )

        mock_get_preset_handler.assert_called_once_with(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1
        )
        mock_client_side_handler.get_filter_func.assert_called_once_with(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_prop_func, mock_kwargs
        )
        self.mock_server_side_handler.get_filters.assert_called_once_with(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, mock_prop_func, mock_kwargs
        )

        self.assertEqual(self.instance._client_side_filter, mock_client_filter_func)
        self.assertEqual(self.instance._server_side_filters, mock_server_filters)

    @raises(ParseQueryError)
    def test_parse_where_filter_already_set(self):
        """
        Tests that parse_where functions expectedly
        method raises ParseQueryError when client_side_filter already set
        """

        self.instance._client_side_filter = "previously-set-func"
        self.instance.parse_where(MockQueryPresets.ITEM_1, MockProperties.PROP_1)

    @raises(QueryPropertyMappingError)
    def test_parse_where_prop_invalid(self):
        """
        Tests that parse_where functions expectedly - where inputs invalid
        method raises QueryPropertyMappingError when prop_handler.get_prop_mapping returns None
        """
        # test if prop_mapping doesn't exist
        self.instance._client_side_filter = None
        self.mock_prop_handler.get_prop_mapping.return_value = None
        self.instance.parse_where(MockQueryPresets.ITEM_1, MockProperties.PROP_1)

    def test_get_preset_handler_valid(self):
        """
        Tests that get_preset_handler functions expectedly - where inputs invalid
        method should return a client_handler that supports a given preset-property pair
        """
        self.mock_client_handler_1.check_supported.return_value = False
        self.mock_client_handler_2.check_supported.return_value = True

        # check when preset found
        res = self.instance._get_preset_handler(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1
        )
        self.assertEqual(res, self.mock_client_handler_2)

    @raises(QueryPresetMappingError)
    def test_get_preset_handler_invalid(self):
        """
        Tests that get_preset_handler functions expectedly - where inputs invalid
        method raises QueryPresetMappingError when no client-side handler available has mapping for preset-property pair
        """
        self.mock_client_handler_1.check_supported.return_value = False
        self.mock_client_handler_2.check_supported.return_value = False
        self.instance._get_preset_handler(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1
        )
