import unittest
from unittest.mock import MagicMock, call
from parameterized import parameterized

from openstack_query.query_server import QueryServer


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

    def test_run_query(self):
        """
        Tests _run_query method works expectedly
        """
        self.conn.identity.projects.return_value = [{"id": "proj1"}, {"id": "proj2"}]

        self.conn.compute.servers.side_effect = [
            ["server1", "server2"],
            ["server3", "server4"],
        ]

        res = self.instance._run_query(self.conn)
        self.conn.identity.projects.assert_called_once()
        self.conn.compute.servers.assert_has_calls(
            [
                call(filters={"all_tenants": True, "project_id": "proj1"}),
                call(filters={"all_tenants": True, "project_id": "proj2"}),
            ]
        )
        self.assertEqual(res, ["server1", "server2", "server3", "server4"])
