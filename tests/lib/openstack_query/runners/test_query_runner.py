import unittest
from unittest.mock import MagicMock, patch

from openstack_query.runners.query_runner import QueryRunner

# pylint:disable=protected-access


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
    def test_run_with_only_client_side_filter(
        self, mock_run_query, mock_apply_client_side_filter
    ):
        """
        Tests that run method functions expectedly - with only client_side_filter_func set
        method should call run_query and run apply_client_side_filter and return results
        """
        mock_run_query.return_value = ["openstack-resource-1", "openstack-resource-2"]
        mock_apply_client_side_filter.return_value = ["openstack-resource-1"]

        mock_client_side_filter_func = MagicMock()
        mock_cloud_domain = MagicMock()
        mock_cloud_domain.name = "test"

        res = self.instance.run(
            cloud_account=mock_cloud_domain,
            client_side_filter_func=mock_client_side_filter_func,
            **{"arg1": "val1", "arg2": "val2"}
        )
        self.mocked_connection.assert_called_once_with("test")

        mock_run_query.assert_called_once_with(
            self.conn, None, **{"arg1": "val1", "arg2": "val2"}
        )
        mock_apply_client_side_filter.assert_called_once_with(
            ["openstack-resource-1", "openstack-resource-2"],
            mock_client_side_filter_func,
        )
        mock_client_side_filter_func.assert_not_called()
        self.assertEqual(["openstack-resource-1"], res)

    @patch("openstack_query.runners.query_runner.QueryRunner._run_query")
    def test_run_with_server_side_filters(self, mock_run_query):
        """
        Tests that run method functions expectedly - with server_side_filters set
        method should call run_query and return results
        """
        mock_server_filters = {"server_filter1": "abc", "server_filter2": False}
        mock_run_query.return_value = ["openstack-resource-1"]
        self.instance._run_query = mock_run_query
        mock_client_side_filter_func = MagicMock()
        mock_user_domain = MagicMock()
        mock_user_domain.name = "test"

        res = self.instance.run(
            cloud_account=mock_user_domain,
            client_side_filter_func=mock_client_side_filter_func,
            server_side_filters=mock_server_filters,
            **{"arg1": "val1", "arg2": "val2"}
        )
        self.mocked_connection.assert_called_once_with("test")

        mock_run_query.assert_called_once_with(
            self.conn, mock_server_filters, **{"arg1": "val1", "arg2": "val2"}
        )

        # if we have server-side filters, don't use client_side_filters
        mock_client_side_filter_func.assert_not_called()
        self.assertEqual(["openstack-resource-1"], res)

    @patch("openstack_query.runners.query_runner.QueryRunner._parse_subset")
    @patch("openstack_query.runners.query_runner.QueryRunner._apply_client_side_filter")
    def test_run_with_subset(self, mock_apply_filter_func, mock_parse_subset):
        """
        Tests that run method functions expectedly - with meta param 'from_subset' set
        method should run parse_subset on 'from_subset' values and then apply_client_side_filter and return results
        """
        mock_parse_subset.return_value = [
            "parsed-openstack-resource-1",
            "parsed-openstack-resource-2",
        ]
        mock_apply_filter_func.return_value = ["parsed-openstack-resource-1"]
        mock_client_side_filter_func = MagicMock()
        mock_cloud_domain = MagicMock()
        mock_cloud_domain.name = "test"

        res = self.instance.run(
            cloud_account=mock_cloud_domain,
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

        self.assertEqual(["parsed-openstack-resource-1"], res)

    def test_apply_filter_func(self):
        """
        Tests that apply_filter_func method functions expectedly
        method should iteratively run filter_func on each item and return only those that filter_function returned True
        """
        mock_client_side_filter_func = MagicMock()
        mock_client_side_filter_func.side_effect = [False, True]

        mock_items = ["openstack-resource-1", "openstack-resource-2"]

        res = self.instance._apply_client_side_filter(
            mock_items, mock_client_side_filter_func
        )
        self.assertEqual(["openstack-resource-2"], res)
