import unittest
from unittest.mock import Mock, MagicMock, call, patch
from nose.tools import raises
from parameterized import parameterized
from openstack_query.runners.user_runner import UserRunner

from openstack.identity.v3.user import User

from exceptions.parse_query_error import ParseQueryError

# pylint:disable=protected-access
from enums.user_domains import UserDomains
from exceptions.enum_mapping_error import EnumMappingError


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
    @patch("openstack_query.runners.user_runner.UserRunner._get_user_domain")
    def test_run_query(self, _, mock_filter_kwargs, mock_get_user_domain):
        """
        Tests the _run_query method runs as expected using kwargs

        Args:
            _ (_type_): _description_
            mock_filter_kwargs (Dict[str,str]): mocked dictionary of parameters for the query
        """
        mock_user_list = self.conn.identity.users.return_value = [
            "user1",
            "user2",
            "user3",
        ]
        mock_user = self.conn.identity.users
        res = self.instance._run_query(self.conn, filter_kwargs=mock_filter_kwargs)
        self.assertEqual(res, mock_user_list)
        if mock_filter_kwargs:
            mock_user.assert_called_once_with(**mock_filter_kwargs)
        else:
            mock_user.assert_called_once_with(
                **{"domain_id": mock_get_user_domain.return_value}
            )

    @raises(ParseQueryError)
    def test_run_query_with_from_domain_and_id_given(self):
        """
        Test error is raised when the domain name and domain id is provided at
        the same time
        """
        self.instance._run_query(
            self.conn, filter_kwargs={"domain_id": 1}, from_domain=MagicMock()
        )

    @patch("openstack_query.runners.user_runner.UserRunner._get_user_domain")
    def test_run_query_with_from_domain(self, mock_get_user_domain):
        """
        Test that users searched when domain name is provided
        """
        mock_user_list = self.conn.identity.users.return_value = [
            "user1",
            "user2",
            "user3",
        ]
        mock_user = self.conn.identity.users
        mock_domain = MagicMock()
        res = self.instance._run_query(self.conn, from_domain=mock_domain)
        mock_get_user_domain.assert_called_once_with(self.conn, mock_domain)
        mock_user.assert_called_once_with(
            **{"domain_id": mock_get_user_domain.return_value}
        )
        self.assertEqual(res, mock_user_list)

    @parameterized.expand(
        [(f"test {domain.name.lower()}", domain) for domain in UserDomains]
    )
    def test_get_user_domain(self, _, domain):
        """
        Test that user domains have a mapping and no errors are raised
        """
        self.instance._get_user_domain(self.conn, domain)

    @raises(EnumMappingError)
    def test_get_user_domain_error_raised(self):
        """
        Test that an error is raised if a domain mapping is not found
        """
        self.instance._get_user_domain(self.conn, MagicMock())

    def test_parse_subset(self):
        """
        Tests _parse_subset works expectedly
        method simply checks each value in 'subset' param is of the User type and returns it
        """

        # with one item
        mock_user_1 = MagicMock()
        mock_user_1.__class__ = User
        res = self.instance._parse_subset(self.conn, [mock_user_1])
        self.assertEqual(res, [mock_user_1])

        # with two items
        mock_user_2 = MagicMock()
        mock_user_2.__class__ = User
        res = self.instance._parse_subset(self.conn, [mock_user_1, mock_user_2])
        self.assertEqual(res, [mock_user_1, mock_user_2])

    @raises(ParseQueryError)
    def test_parse_subset_invalid(self):
        """
        Tests _parse_subset works expectedly
        method raises error when provided value which is not of User type
        """
        invalid_user = "invalid-user-obj"
        self.instance._parse_subset(self.conn, [invalid_user])
