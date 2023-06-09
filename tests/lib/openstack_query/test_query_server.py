import unittest
from unittest.mock import MagicMock, call, patch
from parameterized import parameterized

from openstack_query.query_server import QueryServer
from openstack.compute.v2.server import Server


from enums.query.server_properties import ServerProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsInteger,
    QueryPresetsDateTime,
    QueryPresetsString,
)

from tests.lib.openstack_query.test_query_mappings import QueryMappingTests


class QueryServerTests(QueryMappingTests, unittest.TestCase):
    """
    Runs various tests to ensure that QueryServerTests functions expectedly.
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = QueryServer(connection_cls=self.mocked_connection)
        self.conn = self.mocked_connection.return_value.__enter__.return_value

    @parameterized.expand(
        [(f"test {prop.name.lower()}", prop) for prop in ServerProperties]
    )
    def test_property_to_property_func_mapping(self, name, prop):
        """
        Tests that all openstack properties have a property function mapping
        """
        assert self.instance._get_prop(prop)

    @parameterized.expand(
        [
            (f"test {preset.name.lower()}", preset)
            for preset in [
                *QueryPresetsGeneric,
                *QueryPresetsInteger,
                *QueryPresetsDateTime,
                *QueryPresetsString,
            ]
        ]
    )
    def test_preset_to_filter_func_mapping(self, name, preset):
        """
        Tests that all query presets have a default filter function mapping
        """
        assert self.instance._get_default_filter_func(preset)

    @patch("openstack_query.query_server.QueryServer._run_query_on_projects")
    def test_run_query(self, mocked_run_query_on_projects):
        """
        Tests _run_query method works expectedly
        """
        self.conn.identity.projects.return_value = [{"id": "proj1"}, {"id": "proj2"}]
        mocked_run_query_on_projects.return_value = [
            "server1",
            "server2",
            "server3",
            "server4",
        ]

        res = self.instance._run_query(self.conn)
        self.conn.identity.projects.assert_called_once()
        mocked_run_query_on_projects.assert_called_once_with(
            self.conn, [{"id": "proj1"}, {"id": "proj2"}], None
        )
        self.assertEqual(res, ["server1", "server2", "server3", "server4"])

    @patch("openstack_query.query_server.QueryServer._run_query_on_project")
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
        mock_server_1 = MagicMock()
        mock_server_1.__class__ = Server
        res = self.instance._parse_subset([mock_server_1])
        self.assertEqual(res, [mock_server_1])

        mock_server_2 = MagicMock()
        mock_server_2.__class__ = Server
        res = self.instance._parse_subset([mock_server_1, mock_server_2])
        self.assertEqual(res, [mock_server_1, mock_server_2])
