import unittest
from unittest.mock import MagicMock, NonCallableMock, call

import pytest

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

    def test_select_invalid(self):
        """
        Tests select method works expectedly - with no inputs
        method raises ParseQueryError when given no properties
        """
        with pytest.raises(ParseQueryError):
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

    def _run_case_with_various_params(self, data_subset, mock_kwargs):
        """
        Runs a test case with various params preset
        """
        mock_client_filter_func = self.mock_builder.client_side_filter
        mock_server_filters = self.mock_builder.server_side_filters
        mock_parser_results = ["obj1", "obj2"]
        self.mock_parser.run_parser.return_value = mock_parser_results

        if not mock_kwargs:
            mock_kwargs = {}

        res = self.instance.run("test-account", data_subset, **mock_kwargs)
        self.mock_runner.run.assert_called_once_with(
            "test-account",
            mock_client_filter_func,
            mock_server_filters,
            data_subset,
            **mock_kwargs
        )
        self.mock_parser.run_parser.assert_called_once_with(
            self.mock_runner.run.return_value
        )
        self.mock_output.generate_output.assert_called_once_with(["obj1", "obj2"])
        self.assertEqual(res, self.instance)

    def test_run_with_optional_params(self):
        """
        Tests that run method works expectedly - with subset meta_params kwargs
        method should get client_side and server_side filters and forward them to query runner object

        """
        self._run_case_with_various_params(
            data_subset=["obj1", "obj2", "obj3"], mock_kwargs=None
        )

    def test_run_with_kwargs(self):
        """
        Tests that run method works expectedly - with subset kwargs
        method should get client_side and server_side filters and forward them to query runner object

        """
        self._run_case_with_various_params(
            data_subset=None, mock_kwargs={"arg1": "val1", "arg2": "val2"}
        )

    def test_run_with_nothing(self):
        """
        Tests that run method works expectedly - with subset kwargs
        method should get client_side and server_side filters and forward them to query runner object

        """
        self._run_case_with_various_params(None, None)

    def test_run_with_kwargs_and_subset(self):
        """
        Tests that run method works expectedly - with subset kwargs
        method should get client_side and server_side filters and forward them to query runner object

        """
        self._run_case_with_various_params(
            data_subset=["obj1", "obj2", "obj3"],
            mock_kwargs={"arg1": "val1", "arg2": "val2"},
        )

    def test_run_with_parsing_grouped(self):
        """
        Tests that run method works expectedly - with parsing - i.e. grouping into dict
        Should call run_parser to get items - either dict of lists or list and handle them properly
        """
        self.mock_parser.run_parser.return_value = ["obj1", "obj2"]
        self.mock_parser.run_parser.return_value = {
            "group1": ["obj1", "obj2"],
            "group2": ["obj3", "obj4"],
        }
        self.instance.run("cloud_account")
        self.mock_output.generate_output.assert_has_calls(
            [call(["obj1", "obj2"]), call(["obj3", "obj4"])]
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

    def test_sort_by(self):
        """
        Tests that sort_by method functions expectedly
        method should call QueryParser object parse_sort_by() and return results
        """
        mock_sort_by = [("some-prop-enum", False), ("some-prop-enum-2", True)]
        self.instance.sort_by(*mock_sort_by)
        self.instance.parser.parse_sort_by.assert_called_once_with(*mock_sort_by)

    def test_group_by(self):
        """
        Tests that group_by method functions expectedly
        method should call QueryParser object parse_group_by() and return results
        """
        mock_group_by = "some-prop-enum"
        mock_group_ranges = {"group1": ["val1", "val2"], "group2": ["val3"]}
        mock_include_ungrouped_results = False
        self.mock_parser.group_by_prop = None

        self.instance.group_by(
            mock_group_by, mock_group_ranges, mock_include_ungrouped_results
        )
        self.instance.parser.parse_group_by.assert_called_once_with(
            mock_group_by, mock_group_ranges, mock_include_ungrouped_results
        )

    def test_group_by_already_set(self):
        """
        Tests that group_by method functions expectedly
        Should raise error when attempting to set group by when already set
        """
        self.mock_parser.group_by_prop = "prop1"
        with pytest.raises(ParseQueryError):
            self.instance.group_by("prop2")
