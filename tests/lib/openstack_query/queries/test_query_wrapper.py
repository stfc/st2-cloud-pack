import unittest
from unittest.mock import patch, MagicMock
from openstack_query.queries.query_wrapper import QueryWrapper

from tests.lib.openstack_query.mocks.mocked_query_presets import MockQueryPresets
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

from exceptions.parse_query_error import ParseQueryError


class QueryWrapperTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()
        self.mock_prop_handler = MagicMock()
        self.mock_preset_handlers = ["mock_preset_handler1", "mock_preset_handler2"]
        self.mock_kwarg_handler = MagicMock()
        self.instance = QueryWrapper(
            self.mock_prop_handler, self.mock_preset_handlers, self.mock_kwarg_handler
        )

    def test_select(self):
        """
        Tests select method works expectedly and calls parse_select in QueryOutput object
        """
        mock_query_output = MagicMock()
        self.instance.output = mock_query_output

        # with no props
        with self.assertRaises(ParseQueryError):
            _ = self.instance.select()

        # with one prop
        res = self.instance.select(MockProperties.PROP_1)
        mock_query_output.parse_select.assert_called_once_with(
            MockProperties.PROP_1, select_all=False
        )
        self.assertEqual(res, self.instance)

        # with 2 props
        mock_query_output.reset_mock()
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

    def test_where(self):
        """
        Tests that where method works expectedly and calls parse_where in QueryBuilder object
        """
        mock_query_builder = MagicMock()
        self.instance.builder = mock_query_builder

        # no kwargs
        res = self.instance.where(MockQueryPresets.ITEM_1, MockProperties.PROP_1)
        mock_query_builder.parse_where.assert_called_once_with(
            MockQueryPresets.ITEM_1, MockProperties.PROP_1, {}
        )
        self.assertEqual(res, self.instance)

        mock_query_builder.reset_mock()
        # with kwargs
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
        mock_query_builder = MagicMock()
        self.instance.builder = mock_query_builder

        mock_query_runner = MagicMock()
        self.instance.runner = mock_query_runner

        mock_query_output = MagicMock()
        self.instance.output = mock_query_output

        mock_query_builder.filter_func.return_value = "some-filter-func"
        mock_query_builder.filter_kwargs.return_value = "some-filter-kwargs"
        mock_query_runner.run.return_value = "some-runner-output"

        res = self.instance.run("test-account")
        mock_query_builder.filter_func.assert_called_once()
        mock_query_builder.filter_kwargs.assert_called_once()
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
