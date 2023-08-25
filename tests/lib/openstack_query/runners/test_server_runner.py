import unittest
from unittest.mock import MagicMock, call, patch

from openstack_query.runners.server_runner import ServerRunner

from openstack.exceptions import ResourceNotFound
from openstack.compute.v2.server import Server

from exceptions.parse_query_error import ParseQueryError


# pylint:disable=protected-access


class ServerRunnerTests(unittest.TestCase):
    """
    Runs various tests to ensure that ServerRunner functions expectedly.
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        self.marker_prop_func = MagicMock()
        self.instance = ServerRunner(
            marker_prop_func=self.marker_prop_func,
            connection_cls=self.mocked_connection,
        )
        self.conn = self.mocked_connection.return_value.__enter__.return_value

    def test_parse_meta_params_with_from_projects(self):
        """
        Tests _parse_meta_params method works expectedly - with valid from_project argument
        method should iteratively call find_project() to find each project in list and return outputs
        """

        mock_project_identifiers = ["project_id1", "project_id2"]
        self.conn.identity.find_project.side_effect = [
            {"id": "id1"},
            {"id": "id2"},
        ]

        res = self.instance._parse_meta_params(self.conn, mock_project_identifiers)
        self.conn.identity.find_project.assert_has_calls(
            [
                call("project_id1", ignore_missing=False),
                call("project_id2", ignore_missing=False),
            ]
        )
        self.assertListEqual(list(res.keys()), ["projects"])
        self.assertListEqual(res["projects"], ["id1", "id2"])

    def test_parse_meta_params_with_invalid_project_identifier(self):
        """
        Tests _parse_meta_parms method works expectedly - with invalid from_project argument
        method should raise ParseQueryError when an invalid project identifier is given
        (or when project cannot be found)
        """
        mock_project_identifiers = ["project_id3"]
        self.conn.identity.find_project.side_effect = [ResourceNotFound()]
        with self.assertRaises(ParseQueryError):
            self.instance._parse_meta_params(self.conn, mock_project_identifiers)

    @patch("openstack_query.runners.server_runner.ServerRunner._run_paginated_query")
    def test_run_query_with_meta_arg_projects_with_server_side_queries(
            self, mock_run_paginated_query
    ):
        """
        Tests _run_query method works expectedly - when meta arg projects given
        method should for each project:
            - update filter kwargs to include "project_id": <id of project>
            - run _run_paginated_query with updated filter_kwargs
        """
        mock_run_paginated_query.side_effect = [
            ["server1", "server2"],
            ["server3", "server4"],
        ]
        mock_filter_kwargs = {"arg1": "val1"}

        projects = ["project-id1", "project-id2"]

        res = self.instance._run_query(
            self.conn,
            filter_kwargs=mock_filter_kwargs,
            projects=projects,
        )

        for project in projects:
            mock_run_paginated_query.assert_any_call(
                self.conn.compute.servers, {"all_tenants": True, "project_id": project, **mock_filter_kwargs}
            )

        self.assertEqual(res, ["server1", "server2", "server3", "server4"])

    @patch("openstack_query.runners.server_runner.ServerRunner._run_paginated_query")
    def test_run_query_with_meta_arg_projects_with_no_server_queries(
            self, mock_run_paginated_query
    ):
        """
        Tests _run_query method works expectedly - when meta arg projects given
        method should for each project run without any filter kwargs
        """
        mock_run_paginated_query.side_effect = [
            ["server1", "server2"],
            ["server3", "server4"],
        ]
        projects = ["project-id1", "project-id2"]
        res = self.instance._run_query(
            self.conn,
            filter_kwargs={},
            projects=projects

        )

        for project in projects:
            mock_run_paginated_query.assert_any_call(
                self.conn.compute.servers, {"all_tenants": True, "project_id": project}
            )
        self.assertEqual(res, ["server1", "server2", "server3", "server4"])

    def test_run_query_project_meta_arg_preset_duplication(self):
        """
        Tests that an error is raised when run_query is called with filter kwargs which contains project_id and with
        meta_params that also contain projects - i.e there's a mismatch in which projects to search
        """
        with self.assertRaises(ParseQueryError):
            self.instance._run_query(
                self.conn,
                filter_kwargs={"project_id": "proj1"},
                projects=["proj2", "proj3"],
            )

    @patch("openstack_query.runners.server_runner.ServerRunner._run_paginated_query")
    def test_run_query_with_no_meta_args_no_kwargs(
            self, mock_run_paginated_query
    ):
        mock_run_paginated_query.side_effect = [["server1", "server2"]]
        mock_filter_kwargs = {}

        res = self.instance._run_query(self.conn, filter_kwargs=mock_filter_kwargs)

        mock_run_paginated_query.asset_called_once_with(
            self.conn.compute.servers, {"all_tenants": True}
        )
        self.assertEqual(res, ["server1", "server2"])

    @patch("openstack_query.runners.server_runner.ServerRunner._run_paginated_query")
    def test_run_query_with_no_meta_args_with_kwargs(
            self, mock_run_paginated_query
    ):
        mock_run_paginated_query.side_effect = [["server1", "server2"]]
        mock_filter_kwargs = {"arg1": "val1"}

        res = self.instance._run_query(self.conn, filter_kwargs=mock_filter_kwargs)

        mock_run_paginated_query.asset_called_once_with(
            self.conn.compute.servers, {"all_tenants": True,
                                        "arg1": "val1"}
        )
        self.assertEqual(res, ["server1", "server2"])

    def test_parse_subset(self):
        """
        Tests _parse_subset works expectedly
        method simply checks each value in 'subset' param is of the Server type and returns it
        """

        # with one item
        mock_server_1 = MagicMock()
        mock_server_1.__class__ = Server
        res = self.instance._parse_subset(self.conn, [mock_server_1])
        self.assertEqual(res, [mock_server_1])

        # with two items
        mock_server_2 = MagicMock()
        mock_server_2.__class__ = Server
        res = self.instance._parse_subset(self.conn, [mock_server_1, mock_server_2])
        self.assertEqual(res, [mock_server_1, mock_server_2])

    def test_parse_subset_invalid(self):
        """
        Tests _parse_subset works expectedly
        method raises error when provided value which is not of Server type
        """
        invalid_server = "invalid-server-obj"
        with self.assertRaises(ParseQueryError):
            self.instance._parse_subset(self.conn, [invalid_server])
