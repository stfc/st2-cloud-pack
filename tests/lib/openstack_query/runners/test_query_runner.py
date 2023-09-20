import unittest
from unittest.mock import MagicMock, patch
from parameterized import parameterized

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
        self.mock_page_func = self._mock_page_func
        self.instance = QueryRunner(
            marker_prop_func=self.mock_page_func, connection_cls=self.mocked_connection
        )
        self.conn = self.mocked_connection.return_value.__enter__.return_value

    def _mock_page_func(self, mock_obj):
        """simple mock func which returns "id" key from given dict"""
        return mock_obj["id"]

    @patch("openstack_query.runners.query_runner.QueryRunner._apply_client_side_filter")
    @patch("openstack_query.runners.query_runner.QueryRunner._run_query")
    @patch("openstack_query.runners.query_runner.QueryRunner._parse_meta_params")
    def test_run_with_only_client_side_filter(
        self, mock_parse_meta_params, mock_run_query, mock_apply_client_side_filter
    ):
        """
        Tests that run method functions expectedly - with only client_side_filter_func set
        method should call run_query and run apply_client_side_filter and return results
        also tests with no meta-params set
        """
        mock_run_query.return_value = ["openstack-resource-1", "openstack-resource-2"]
        mock_apply_client_side_filter.return_value = ["openstack-resource-1"]

        mock_client_side_filter_func = MagicMock()
        mock_cloud_domain = MagicMock()

        res = self.instance.run(
            cloud_account=mock_cloud_domain,
            client_side_filter_func=mock_client_side_filter_func,
        )
        self.mocked_connection.assert_called_once_with(mock_cloud_domain)

        mock_parse_meta_params.assert_not_called()
        mock_run_query.assert_called_once_with(self.conn, None)

        mock_apply_client_side_filter.assert_called_once_with(
            ["openstack-resource-1", "openstack-resource-2"],
            mock_client_side_filter_func,
        )
        mock_client_side_filter_func.assert_not_called()
        self.assertEqual(["openstack-resource-1"], res)

    @patch("openstack_query.runners.query_runner.QueryRunner._run_query")
    @patch("openstack_query.runners.query_runner.QueryRunner._parse_meta_params")
    def test_run_with_server_side_filters(self, mock_parse_meta_params, mock_run_query):
        """
        Tests that run method functions expectedly - with server_side_filters set
        method should call run_query and return results
        """
        mock_server_filters = {"server_filter1": "abc", "server_filter2": False}
        mock_run_query.return_value = ["openstack-resource-1"]
        self.instance._run_query = mock_run_query
        mock_client_side_filter_func = MagicMock()
        mock_user_domain = MagicMock()

        mock_parse_meta_params.return_value = {
            "parsed_arg1": "val1",
            "parsed_arg2": "val2",
        }

        res = self.instance.run(
            cloud_account=mock_user_domain,
            client_side_filter_func=mock_client_side_filter_func,
            server_side_filters=mock_server_filters,
            **{"arg1": "val1", "arg2": "val2"}
        )
        self.mocked_connection.assert_called_once_with(mock_user_domain)

        mock_parse_meta_params.assert_called_once_with(
            self.conn, **{"arg1": "val1", "arg2": "val2"}
        )

        mock_run_query.assert_called_once_with(
            self.conn,
            mock_server_filters,
            **{"parsed_arg1": "val1", "parsed_arg2": "val2"}
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

        res = self.instance.run(
            cloud_account=mock_cloud_domain,
            client_side_filter_func=mock_client_side_filter_func,
            from_subset=["openstack-resource-1", "openstack-resource-2"],
        )
        self.mocked_connection.assert_called_once_with(mock_cloud_domain)

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

    @parameterized.expand(
        [
            ("call terminated with no rounds - (empty list)", [[]]),
            (
                "call terminates after one round",
                [
                    [
                        {"id": "marker1"},
                    ],
                    [
                        {"id": "out"},
                    ],
                    [],
                ],
            ),
            (
                "call terminates after two rounds",
                [
                    [
                        {"id": "marker1"},
                    ],
                    [
                        {"id": "marker2"},
                    ],
                    [
                        {"id": "out"},
                    ],
                    [],
                ],
            ),
        ]
    )
    def test_run_paginated_query(self, _, mock_out):
        """
        tests that run_paginated_query works expectedly - with no rounds, one round, and two rounds of pagination
        mocked paginated call simulates the effect of retrieving a list of values up to a limit and then calling the
        same call again with a "marker" set to the last seen item to continue reading
        """

        def _mock_prop_func(resource):
            return resource["id"]

        mock_paginated_call = MagicMock()
        mock_paginated_call.side_effect = mock_out
        expected_out = [item for sublist in mock_out for item in sublist]
        self.instance._page_marker_prop_func = MagicMock(wraps=_mock_prop_func)

        # set round to 1, so new calls begins after returning one value
        self.instance._LIMIT_FOR_PAGINATION = 1
        self.instance._PAGINATION_CALL_LIMIT = 10

        mock_server_side_filters = {"arg1": "val1", "arg2": "val2"}
        res = self.instance._run_paginated_query(
            mock_paginated_call, mock_server_side_filters
        )
        self.assertEqual(res, expected_out)
