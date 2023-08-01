import unittest
from unittest.mock import Mock, MagicMock, call, patch
from nose.tools import raises
from parameterized import parameterized
from openstack_query.runners.user_runner import UserRunner

from openstack.exceptions import ResourceNotFound
from openstack.compute.v2.server import Server
from openstack.identity.v3.user import User

from exceptions.parse_query_error import ParseQueryError

# pylint:disable=protected-access


class RunnerTests(unittest.TestCase):
    """
    Runs various tests to ensure that UserRunner functions expectedly.
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = UserRunner(connection_cls=self.mocked_connection)
        self.conn = self.mocked_connection.return_value.__enter__.return_value

    @parameterized.expand(
        [
            ("contains kwargs and domain", {"domain_id": 1}),
            ("contains kwargs no domain id", {"arg1": 12, "arg2": 42}),
            ("no kwargs", None),
        ]
    )
    def test_run_query(self, _, mock_filter_kwargs):
        """
        Tests the _run_query method runs as expected using kwargs

        Args:
            _ (_type_): _description_
            mock_filter_kwargs (Dict[str,str]): mocked dictionary of parameters for the query
        """
        mock_user_list = self.conn.identity.v3.users.return_value = [
            "user1",
            "user2",
            "user3",
        ]
        res = self.instance._run_query(self.conn, filter_kwargs=mock_filter_kwargs)
        self.assertEqual(res, mock_user_list)
        mock_user_list.assert_called_once_with(**mock_filter_kwargs)
