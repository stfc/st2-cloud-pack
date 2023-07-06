import unittest
from unittest.mock import patch, MagicMock
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
        Tests select method works expectedly and calls parse_select in QueryOutput object - no props given
        """
        self.instance.select()

    def test_select_with_one_prop(self):
        """
        Tests select method works expectedly and calls parse_select in QueryOutput object - one prop given
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
        Tests select method works expectedly and calls parse_select in QueryOutput object - many props given
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
        Tests select all method works expectedly and calls parse_select in QueryOutput object
        """
        mock_query_output = MagicMock()
        self.instance.output = mock_query_output
        res = self.instance.select_all()
        mock_query_output.parse_select.assert_called_once_with(select_all=True)
        self.assertEqual(res, self.instance)

    def test_where_no_kwargs(self):
        """
        Tests that where method works expectedly and calls parse_where in QueryBuilder object - when no kwargs given
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
        Tests that where method works expectedly and calls parse_where in QueryBuilder object - with kwargs given
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
        """
        mock_query_builder = MagicMock()
        self.instance.builder = mock_query_builder

        mock_query_runner = MagicMock()
        self.instance.runner = mock_query_runner

        mock_query_output = MagicMock()
        self.instance.output = mock_query_output

        mock_query_builder.client_side_filter.return_value = "some-filter-func"
        mock_query_builder.server_side_filters.return_value = "some-filter-kwargs"
        mock_query_runner.run.return_value = "some-runner-output"

        res = self.instance.run("test-account")
        mock_query_builder.client_side_filter.assert_called_once()
        mock_query_builder.server_side_filters.assert_called_once()
        mock_query_runner.run.assert_called_once_with(
            "test-account", "some-filter-func", "some-filter-kwargs", None
        )
        mock_query_output.generate_output.assert_called_once_with("some-runner-output")

        self.assertEqual(res, self.instance)

    def test_to_list(self):
        mock_query_output = MagicMock()
        self.instance.output = mock_query_output
        self.instance.output.results.return_value = "list-out"

        # when as_objects false
        self.assertEqual(self.instance.to_list(), "list-out")

        # when as_objects true
        self.instance._query_results = "objects-out"
        self.assertEqual(self.instance.to_list(as_objects=True), "objects-out")

    def test_to_string(self):
        mock_query_output = MagicMock()
        self.instance.output = mock_query_output
        self.instance.output.to_string.return_value = "string-out"
        self.assertEqual(self.instance.to_string(), "string-out")

    def test_to_html(self):
        mock_query_output = MagicMock()
        self.instance.output = mock_query_output
        self.instance.output.to_html.return_value = "html-out"
        self.assertEqual(self.instance.to_html(), "html-out")
