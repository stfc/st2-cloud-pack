import unittest
from openstack.exceptions import ResourceNotFound

from unittest.mock import Mock, MagicMock, call, patch
from openstack_query.runners.server_runner import ServerRunner

from openstack.compute.v2.server import Server
from openstack.identity.v3.project import Project
from exceptions.parse_query_error import ParseQueryError
from nose.tools import raises


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

    def test_get_projects_get_all(self):
        """
        Tests _get_projects gets all projects when project param empty
        """
        self.conn.identity.projects.return_value = ["project1", "project2"]
        res = self.instance._get_projects(self.conn)
        self.conn.identity.projects.assert_called_once()
        self.assertEqual(res, ["project1", "project2"])

    def test_get_projects_with_string_project_identifiers(self):
        """
        Tests _get_project method works when projects param not empty
        """
        mock_project_identifiers = ["project_id1", "project_id2"]
        self.conn.identity.find_project.side_effect = [
            "project1",
            "project2",
        ]
        res = self.instance._get_projects(self.conn, mock_project_identifiers)
        self.conn.identity.find_project.assert_has_calls(
            [
                call("project_id1", ignore_missing=False),
                call("project_id2", ignore_missing=False),
            ]
        )
        self.assertEqual(res, ["project1", "project2"])

    def test_get_projects_with_project_objects(self):
        """
        Tests _get_project method works when projects param not empty
        """
        mock_proj1 = Mock()
        mock_proj1.__class__ = Project

        mock_proj2 = Mock()
        mock_proj2.__class__ = Project

        mock_project_identifiers = [mock_proj1, mock_proj2]
        res = self.instance._get_projects(self.conn, mock_project_identifiers)
        self.assertEqual(res, [mock_proj1, mock_proj2])

    @raises(ParseQueryError)
    def test_get_projects_with_invalid_list(self):
        """
        Tests _get_project method raises error when projects param has invalid entry
        """
        self.conn.identity.find_project.side_effect = [ResourceNotFound()]
        _ = self.instance._get_projects(self.conn, ["invalid-identifier"])

    @patch("openstack_query.runners.server_runner.ServerRunner._get_projects")
    @patch("openstack_query.runners.server_runner.ServerRunner._run_query_on_projects")
    def test_run_query(self, mock_run_query_on_projects, mock_get_projects):
        """
        Tests _run_query method works expectedly
        """
        mock_get_projects.return_value = ["project1", "project2"]
        mock_run_query_on_projects.return_value = {
            "project1": ["server1", "server2"],
            "project2": ["server3", "server4"],
        }

        res = self.instance._run_query(
            self.conn, filter_kwargs=None, from_projects=["project-id1", "project-id2"]
        )
        mock_get_projects.assert_called_once_with(
            self.conn, ["project-id1", "project-id2"]
        )
        mock_run_query_on_projects.assert_called_once_with(
            self.conn, ["project1", "project2"], None
        )
        self.assertEqual(res, ["server1", "server2", "server3", "server4"])

    @patch("openstack_query.runners.server_runner.ServerRunner._run_query_on_project")
    def test_run_query_from_projects(self, mock_run_query_on_project):
        """
        Tests _run_query_on_projects works expectedly
        """
        project1 = {"id": "project-id1"}
        project2 = {"id": "project-id2"}
        mock_project_list = [project1, project2]

        # Mock the return value of _run_query_on_project
        mock_run_query_on_project.side_effect = [
            ["server1", "server2"],
            ["server3", "server4"],
        ]

        res = self.instance._run_query_on_projects(self.conn, mock_project_list)
        mock_run_query_on_project.assert_has_calls(
            [call(self.conn, project1, None), call(self.conn, project2, None)]
        )
        self.assertEqual(
            res,
            {
                "project-id1": ["server1", "server2"],
                "project-id2": ["server3", "server4"],
            },
        )

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
