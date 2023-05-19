import unittest
from unittest.mock import patch, MagicMock, call, NonCallableMock
from enum import Enum, auto
from nose.tools import assert_raises, raises

from exceptions.parse_query_error import ParseQueryError
from openstack_query.query_server import QueryServer


class QueryServerTests(unittest.TestCase):
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

    def test_run_query(self):
        """
        Tests _run_query method works expectedly
        """
        self.conn.identity.projects.return_value = [
            {'id': 'proj1'},
            {'id': 'proj2'}
        ]

        self.conn.compute.servers.side_effect = [
            ['server1', 'server2'],
            ['server3', 'server4']
        ]

        res = self.instance._run_query(self.conn)
        self.conn.identity.projects.assert_called_once()
        self.conn.compute.servers.assert_has_calls([
            call(
                filters={'all_tenants': True, 'project_id': 'proj1'}
            ),
            call(
                filters={'all_tenants': True, 'project_id': 'proj2'}
            )
        ])
        self.assertEqual(res, ['server1', 'server2', 'server3', 'server4'])
