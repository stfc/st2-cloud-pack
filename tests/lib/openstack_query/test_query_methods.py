import unittest
from unittest.mock import MagicMock, NonCallableMock
from openstack_query.query_methods import QueryMethods

from nose.tools import raises

from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

from exceptions.parse_query_error import ParseQueryError


class QueryMethodsTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()
        self.mock_builder = MagicMock()
        self.mock_runner = MagicMock()
        self.mock_output = MagicMock()
        self.instance = QueryMethods(
            self.mock_builder,
            self.mock_runner,
            self.mock_output,
        )

    @raises(ParseQueryError)
    def test_select_invalid(self):
        """
        Tests select method works expectedly - with no inputs
        method raises ParseQueryError when given no properties
        """
        self.instance.select()

    def test_select_with_one_prop(self):
        """
        Tests select method works expectedly - with one prop
        method should forward prop to parse_select in QueryOutput object
        """
        mock_query_output = MagicMock()
        self.instance.output = mock_query_output

        res = self.instance.select(MockProperties.PROP_1)
        mock_query_output.parse_select.assert_called_once_with(
            MockProperties.PROP_1, select_all=False
        )
        self.assertEqual(res, self.instance)

    def test_select_with_many_props(self):
        """
        Tests select method works expectedly - with multiple prop
        method should forward props to parse_select in QueryOutput object
        """
        mock_query_output = MagicMock()
        self.instance.output = mock_query_output

        res = self.instance.select(MockProperties.PROP_1, MockProperties.PROP_2)
        mock_query_output.parse_select.assert_called_once_with(
            MockProperties.PROP_1, MockProperties.PROP_2, select_all=False
        )
        self.assertEqual(res, self.instance)

    def test_select_all(self):
        """
        Tests select all method works expectedly
        method should call parse_select in QueryOutput object
        """
        mock_query_output = MagicMock()
        self.instance.output = mock_query_output
        res = self.instance.select_all()
        mock_query_output.parse_select.assert_called_once_with(select_all=True)
        self.assertEqual(res, self.instance)

    def test_where_no_kwargs(self):
        """
        Tests that where method works expectedly
        method should forward to parse_where in QueryBuilder object - with no kwargs given
        """
        mock_query_builder = MagicMock()
        self.instance.builder = mock_query_builder

        res = self.instance.where(MockQueryPresets.ITEM_1, MockProperties.PROP_1)
        mock_query_builder.parse_where.assert_called_once_with(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, {}
        )
        self.assertEqual(res, self.instance)

    def test_where_with_kwargs(self):
        """
        Tests that where method works expectedly
        method should forward to parse_where in QueryBuilder object - with kwargs given
        """
        mock_query_builder = MagicMock()
        self.instance.builder = mock_query_builder
        res = self.instance.where(
            MockQueryPresets.ITEM_2, MockProperties.PROP_2, arg1="val1", arg2="val2"
        )
        mock_query_builder.parse_where.assert_called_once_with(
            MockQueryPresets.ITEM_2,
            MockProperties.PROP_2,
            {"arg1": "val1", "arg2": "val2"},
        )
        self.assertEqual(res, self.instance)

    def test_run(self):
        """
        Tests that run method works expectedly
        method should get client_side and server_side filters and forward them to query runner object
        """
        mock_query_builder = MagicMock()
        self.instance.builder = mock_query_builder

        mock_query_runner = MagicMock()
        self.instance.runner = mock_query_runner

        mock_query_output = MagicMock()
        self.instance.output = mock_query_output

        mock_client_filter_func = MagicMock()
        mock_query_builder.client_side_filter = mock_client_filter_func

        mock_server_filters = NonCallableMock()
        mock_query_builder.server_side_filters = mock_server_filters

        mock_query_results = NonCallableMock()
        mock_query_runner.run.return_value = mock_query_results

        res = self.instance.run("test-account")
        mock_query_runner.run.assert_called_once_with(
            "test-account", mock_client_filter_func, mock_server_filters, None
        )
        mock_query_output.generate_output.assert_called_once_with(mock_query_results)

        self.assertEqual(res, self.instance)

    def test_to_list_as_objects_false(self):
        """
        Tests that to_list method functions expectedly
        method should call QueryOutput object results() if as_objects input is false,
        """
        mock_query_output = MagicMock()
        mock_query_results = NonCallableMock()
        self.instance.output = mock_query_output
        self.instance.output.results = mock_query_results
        self.assertEqual(self.instance.to_list(), mock_query_results)

    def test_to_list_as_objects_true(self):
        """
        Tests that to_list method functions expectedly
        method should return query_results internal attribute if as_objects input is true,
        """
        mock_query_results_list = ["object-1", "object-2"]
        self.instance._query_results = mock_query_results_list
        self.assertEqual(
            self.instance.to_list(as_objects=True), mock_query_results_list
        )

    def test_to_string(self):
        """
        Tests that to_string method functions expectedly
        method should call QueryOutput object to_string() and return results
        """
        mock_query_output = MagicMock()
        self.instance.output = mock_query_output
        self.instance.output.to_string.return_value = "string-out"
        self.assertEqual(self.instance.to_string(), "string-out")

    def test_to_html(self):
        """
        Tests that to_html method functions expectedly
        method should call QueryOutput object to_html() and return results
        """
        mock_query_output = MagicMock()
        self.instance.output = mock_query_output
        self.instance.output.to_html.return_value = "html-out"
        self.assertEqual(self.instance.to_html(), "html-out")
