import unittest
from unittest.mock import MagicMock, NonCallableMock, call
from parameterized import parameterized
from nose.tools import raises

from openstack_query.query_methods import QueryMethods

from exceptions.parse_query_error import ParseQueryError
from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties


class QueryMethodsTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()
        self.mock_builder = MagicMock()
        self.mock_runner = MagicMock()
        self.mock_parser = MagicMock()
        self.mock_output = MagicMock()
        self.instance = QueryMethods(
            self.mock_builder,
            self.mock_runner,
            self.mock_parser,
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

    @parameterized.expand([
        ("with kwargs", None, {"arg1": "val1", "arg2": "val2"}),
        ("with from_subset", ["obj1", "obj2", "obj3"], None),
        ("with no kwargs and no subset", None, None),
    ])
    def test_run_with_optional_params(self, _, mock_from_subset, mock_kwargs):
        """
        Tests that run method works expectedly - with subset and/or meta_params kwargs
        method should get client_side and server_side filters and forward them to query runner object

        """
        mock_client_filter_func = self.mock_builder.client_side_filter
        mock_server_filters = self.mock_builder.server_side_filters
        mock_parser_results = ["obj1", "obj2"]
        self.mock_parser.run_parser.return_value = mock_parser_results

        if not mock_kwargs:
            mock_kwargs = {}

        res = self.instance.run("test-account", mock_from_subset, **mock_kwargs)
        self.mock_runner.run.assert_called_once_with(
            "test-account",
            mock_client_filter_func,
            mock_server_filters,
            mock_from_subset,
            **mock_kwargs
        )
        self.mock_parser.run_parser.assert_called_once_with(
            self.mock_runner.run.return_value
        )
        self.mock_output.generate_output.assert_called_once_with(
            ["obj1", "obj2"]
        )

    @parameterized.expand([
        ("parser outputs grouped results", True),
        ("parser outputs list results", False),
    ])
    def test_run_with_parsing(self, _, parse_output_as_dict):
        """
        Tests that run method works expectedly - with parsing - grouping and sorting
        Should call run_parser to get items - either dict of lists or list and handle them properly

        """
        self.mock_parser.run_parser.return_value = ["obj1", "obj2"]
        if parse_output_as_dict:
            self.mock_parser.run_parser.return_value = {
                "group1": ["obj1", "obj2"],
                "group2": ["obj3", "obj4"],
            }

        self.instance.run("cloud_account")

        if parse_output_as_dict:
            self.mock_output.generate_output.assert_has_calls(
                [call(["obj1", "obj2"]), call(["obj3", "obj4"])]
            )
        else:
            self.mock_output.generate_output.assert_called_once_with(
                ["obj1", "obj2"]
            )

    def test_to_list_as_objects_false(self):
        """
        Tests that to_list method functions expectedly
        method should return _query_results attribute when as_objects is false
        """
        # pylint: disable=protected-access
        mock_query_results = NonCallableMock()
        self.instance._query_results = mock_query_results
        self.assertEqual(self.instance.to_list(), mock_query_results)

    def test_to_list_as_objects_true(self):
        """
        Tests that to_list method functions expectedly
        method should return _query_results_as_objects attribute when as_objects is true
        """
        # pylint: disable=protected-access
        mock_query_results_as_obj = NonCallableMock()
        self.instance._query_results_as_objects = mock_query_results_as_obj
        self.assertEqual(
            self.instance.to_list(as_objects=True), mock_query_results_as_obj
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
