import unittest
from unittest.mock import MagicMock, patch

from openstack_query.runners.query_runner import QueryRunner


class QueryRunnerTests(unittest.TestCase):
    @patch.multiple(QueryRunner, __abstractmethods__=set())
    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = QueryRunner(connection_cls=self.mocked_connection)
        self.conn = self.mocked_connection.return_value.__enter__.return_value

    @patch("openstack_query.runners.query_runner.QueryRunner._apply_filter_func")
    @patch("openstack_query.runners.query_runner.QueryRunner._run_query")
    def test_run_only_filter_func(self, mock_run_query, mock_apply_filter_func):

        mock_run_query.return_value = ["openstack-resource-1", "openstack-resource-2"]
        mock_apply_filter_func.return_value = ["filtered-openstack-resource"]

        res = self.instance.run(
            cloud_account="test",
            filter_func="some-filter-func",
            **{"arg1": "val1", "arg2": "val2"}
        )
        self.mocked_connection.assert_called_once_with("test")

        mock_run_query.assert_called_once_with(
            self.conn, None, **{"arg1": "val1", "arg2": "val2"}
        )
        mock_apply_filter_func.assert_called_once_with(
            ["openstack-resource-1", "openstack-resource-2"], "some-filter-func"
        )
        self.assertEqual(["filtered-openstack-resource"], res)

    @patch("openstack_query.runners.query_runner.QueryRunner._run_query")
    def test_run_with_filter_kwargs(self, mock_run_query):

        mock_run_query.return_value = ["kwarg-filtered-openstack-resource"]
        self.instance._run_query = mock_run_query

        res = self.instance.run(
            cloud_account="test",
            filter_func="some-filter-func",
            filter_kwargs="some-filter-kwargs",
            **{"arg1": "val1", "arg2": "val2"}
        )
        self.mocked_connection.assert_called_once_with("test")

        mock_run_query.assert_called_once_with(
            self.conn, "some-filter-kwargs", **{"arg1": "val1", "arg2": "val2"}
        )

        self.assertEqual(["kwarg-filtered-openstack-resource"], res)

    @patch("openstack_query.runners.query_runner.QueryRunner._parse_subset")
    @patch("openstack_query.runners.query_runner.QueryRunner._apply_filter_func")
    def test_run_with_subset(self, mock_apply_filter_func, mock_parse_subset):
        mock_parse_subset.return_value = [
            "parsed-openstack-resource-1",
            "parsed-openstack-resource-2",
        ]
        mock_apply_filter_func.return_value = ["filtered-openstack-resource"]

        res = self.instance.run(
            cloud_account="test",
            filter_func="some-filter-func",
            from_subset=["openstack-resource-1", "openstack-resource-2"],
        )
        self.mocked_connection.assert_called_once_with("test")

        mock_parse_subset.assert_called_once_with(
            self.conn, ["openstack-resource-1", "openstack-resource-2"]
        )

        mock_apply_filter_func.assert_called_once_with(
            ["parsed-openstack-resource-1", "parsed-openstack-resource-2"],
            "some-filter-func",
        )

        self.assertEqual(["filtered-openstack-resource"], res)

    def test_apply_filter_func(self):
        mock_filter_func = MagicMock()
        mock_filter_func.side_effect = [False, True]

        mock_items = ["openstack-resource-1", "openstack-resource-2"]

        res = self.instance._apply_filter_func(mock_items, mock_filter_func)
        self.assertEqual(["openstack-resource-2"], res)
