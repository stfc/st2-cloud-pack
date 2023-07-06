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

    @patch("openstack_query.runners.query_runner.QueryRunner._apply_client_side_filter")
    @patch("openstack_query.runners.query_runner.QueryRunner._run_query")
    def test_run_only_filter_func(self, mock_run_query, mock_apply_filter_func):
        mock_run_query.return_value = ["openstack-resource-1", "openstack-resource-2"]
        mock_apply_filter_func.return_value = ["filtered-openstack-resource"]
        mock_client_side_filter_func = MagicMock()

        res = self.instance.run(
            cloud_account="test",
            client_side_filter_func=mock_client_side_filter_func,
            **{"arg1": "val1", "arg2": "val2"}
        )
        self.mocked_connection.assert_called_once_with("test")

        mock_run_query.assert_called_once_with(
            self.conn, None, **{"arg1": "val1", "arg2": "val2"}
        )
        mock_apply_filter_func.assert_called_once_with(
            ["openstack-resource-1", "openstack-resource-2"],
            mock_client_side_filter_func,
        )
        mock_client_side_filter_func.assert_not_called()
        self.assertEqual(["filtered-openstack-resource"], res)

    @patch("openstack_query.runners.query_runner.QueryRunner._run_query")
    def test_run_with_server_side_filters(self, mock_run_query):
        mock_run_query.return_value = ["kwarg-filtered-openstack-resource"]
        self.instance._run_query = mock_run_query
        mock_client_side_filter_func = MagicMock()

        res = self.instance.run(
            cloud_account="test",
            client_side_filter_func=mock_client_side_filter_func,
            server_side_filters="some-filter-kwargs",
            **{"arg1": "val1", "arg2": "val2"}
        )
        self.mocked_connection.assert_called_once_with("test")

        mock_run_query.assert_called_once_with(
            self.conn, "some-filter-kwargs", **{"arg1": "val1", "arg2": "val2"}
        )

        # if we have server-side filters, don't use client_side_filters
        mock_client_side_filter_func.assert_not_called()
        self.assertEqual(["kwarg-filtered-openstack-resource"], res)

    @patch("openstack_query.runners.query_runner.QueryRunner._parse_subset")
    @patch("openstack_query.runners.query_runner.QueryRunner._apply_client_side_filter")
    def test_run_with_subset(self, mock_apply_filter_func, mock_parse_subset):
        mock_parse_subset.return_value = [
            "parsed-openstack-resource-1",
            "parsed-openstack-resource-2",
        ]
        mock_apply_filter_func.return_value = ["filtered-openstack-resource"]
        mock_client_side_filter_func = MagicMock()

        res = self.instance.run(
            cloud_account="test",
            client_side_filter_func=mock_client_side_filter_func,
            from_subset=["openstack-resource-1", "openstack-resource-2"],
        )
        self.mocked_connection.assert_called_once_with("test")

        mock_parse_subset.assert_called_once_with(
            self.conn, ["openstack-resource-1", "openstack-resource-2"]
        )

        mock_apply_filter_func.assert_called_once_with(
            ["parsed-openstack-resource-1", "parsed-openstack-resource-2"],
            mock_client_side_filter_func,
        )

        self.assertEqual(["filtered-openstack-resource"], res)

    def test_apply_filter_func(self):
        mock_client_side_filter_func = MagicMock()
        mock_client_side_filter_func.side_effect = [False, True]

        mock_items = ["openstack-resource-1", "openstack-resource-2"]

        res = self.instance._apply_client_side_filter(
            mock_items, mock_client_side_filter_func
        )
        self.assertEqual(["openstack-resource-2"], res)
