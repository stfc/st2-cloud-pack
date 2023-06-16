import unittest
from unittest.mock import Mock, MagicMock, call, patch
from openstack_query.runners.server_runner import ServerRunner

from openstack.compute.v2.server import Server
from openstack.identity.v3.project import Project
from exceptions.parse_query_error import ParseQueryError


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
        self.instance = ServerRunner(connection_cls=self.mocked_connection)
        self.conn = self.mocked_connection.return_value.__enter__.return_value

    @patch("openstack_query.runners.server_runner.ServerRunner._run_query_on_projects")
    def test_run_query(self, mock_run_query_on_projects):
        """
        Tests _run_query method works expectedly
        """
        self.conn.identity.projects.return_value = [{"id": "proj1"}, {"id": "proj2"}]
        mock_run_query_on_projects.return_value = [
            "server1",
            "server2",
            "server3",
            "server4",
        ]

        res = self.instance._run_query(self.conn, filter_kwargs=None)
        self.conn.identity.projects.assert_called_once()
        mock_run_query_on_projects.assert_called_once_with(
            self.conn, [{"id": "proj1"}, {"id": "proj2"}], None
        )
        self.assertEqual(res, ["server1", "server2", "server3", "server4"])

    @patch("openstack_query.runners.server_runner.ServerRunner._run_query_on_projects")
    def test_run_query_with_from_projects(self, mock_run_query_on_projects):
        """
        Tests _run_query method works when from_project kwarg set
        """
        mock_proj1 = Mock()
        mock_proj1.__class__ = Project

        mock_proj2 = Mock()
        mock_proj2.__class__ = Project

        mock_run_query_on_projects.return_value = [
            "server1",
            "server2",
            "server3",
            "server4",
        ]

        mock_from_projects = [mock_proj1, mock_proj2]
        res = self.instance._run_query(self.conn, from_projects=mock_from_projects)
        mock_run_query_on_projects(self.conn, [mock_proj1, mock_proj2], None)
        self.assertEqual(res, ["server1", "server2", "server3", "server4"])

    def test_run_query_with_from_projects_invalid(self):
        """
        Tests that method fails when given from_projects kwarg which is invalid
        """

        # when from_project contains a non-project object
        with self.assertRaises(ParseQueryError):
            _ = self.instance._run_query(self.conn, from_projects=["invalid-obj"])

        # when from_project is empty list
        with self.assertRaises(ParseQueryError):
            _ = self.instance._run_query(self.conn, from_projects=[])

    @patch("openstack_query.runners.server_runner.ServerRunner._run_query_on_project")
    def test_run_query_from_projects(self, mock_run_query_on_project):
        """
        Tests _run_query_on_projects works expectedly
        """
        project1 = MagicMock()
        project2 = MagicMock()
        mock_project_list = [project1, project2]

        # Mock the return value of _run_query_on_project
        mock_run_query_on_project.side_effect = [["server1"], ["server2"]]

        res = self.instance._run_query_on_projects(self.conn, mock_project_list)
        mock_run_query_on_project.assert_has_calls(
            [call(self.conn, project1, None), call(self.conn, project2, None)]
        )
        self.assertEqual(res, ["server1", "server2"])

    def test_run_query_on_project(self):
        """
        Tests _run_query_on_project works expectedly
        """
        mock_project = {"id": "project1"}
        self.conn.compute.servers.return_value = [{"id": "server1"}, {"id": "server2"}]
        res = self.instance._run_query_on_project(self.conn, mock_project)
        self.conn.compute.servers.assert_called_once_with(
            filters={"project_id": "project1", "all_tenants": True}
        )
        self.assertEqual(res, [{"id": "server1"}, {"id": "server2"}])

    def test_parse_subset(self):
        """
        Tests _parse_subset works expectedly
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
