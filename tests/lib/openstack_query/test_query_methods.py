import unittest
from unittest.mock import MagicMock, NonCallableMock
from nose.tools import raises

from openstack_query.query_methods import QueryMethods

from exceptions.parse_query_error import ParseQueryError
from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


class QueryMethodsTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()
        self.mock_builder = MagicMock()
        self.mock_executer = MagicMock()
        self.mock_parser = MagicMock()
        self.mock_output = MagicMock()
        self.instance = QueryMethods(
            self.mock_builder,
            self.mock_executer,
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

    def test_run(self):
        """
        Tests that run method works expectedly
        method should forward to run_query in QueryExecuter object
        """
        self.mock_executer.run_query.return_value = (
            "results-as-objects",
            "results-as-string",
        )

        res = self.instance.run(
            cloud_account="test-account",
            from_subset=["obj1", "obj2", "obj3"],
            **{"arg1": "val1"}
        )
        self.mock_executer.set_filters.assert_called_once_with(
            client_side_filter_func=self.mock_builder.client_side_filter,
            server_side_filters=self.mock_builder.server_side_filters,
        )

        self.mock_executer.set_parse_func.assert_called_once_with(
            parser_func=self.mock_parser.run_parser
        )

        self.mock_executer.set_output_func.assert_called_once_with(
            output_func=self.mock_output.generate_output
        )

        self.mock_executer.run_query.assert_called_once_with(
            cloud_account="test-account",
            from_subset=["obj1", "obj2", "obj3"],
            **{"arg1": "val1"}
        )

        self.instance._query_results_as_objects = "results-as-objects"
        self.instance._query_results = "results-as-string"
        self.assertEqual(res, self.instance)

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

    @raises(ParseQueryError)
    def test_group_by_already_set(self):
        """
        Tests that group_by method functions expectedly
        Should raise error when attempting to set group by when already set
        """
        self.mock_parser.group_by_prop = "prop1"
        self.instance.group_by("prop2")
