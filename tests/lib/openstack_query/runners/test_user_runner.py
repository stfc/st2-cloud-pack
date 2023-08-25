import unittest
from unittest.mock import MagicMock, patch
from nose.tools import raises
from parameterized import parameterized

from openstack_query.runners.user_runner import UserRunner
from openstack.identity.v3.user import User

from exceptions.parse_query_error import ParseQueryError
from exceptions.enum_mapping_error import EnumMappingError

from enums.user_domains import UserDomains

# pylint:disable=protected-access


class UserRunnerTests(unittest.TestCase):
    """
    Runs various tests to ensure that UserRunner functions expectedly.
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        self.marker_prop_func = MagicMock()
        self.instance = UserRunner(
            marker_prop_func=self.marker_prop_func,
            connection_cls=self.mocked_connection,
        )
        self.conn = self.mocked_connection.return_value.__enter__.return_value

    @patch("openstack_query.runners.user_runner.UserRunner._get_user_domain")
    def test_parse_meta_params_with_from_domain(self, mock_get_user_domain):
        """
        Tests _parse_meta_params method works expectedly - with valid from_domain argument
        method should get domain id from a UserDomain enum by calling get_user_domain
        """

        mock_domain_enum = UserDomains.DEFAULT
        mock_get_user_domain.return_value = "default-domain-id"

        res = self.instance._parse_meta_params(self.conn, from_domain=mock_domain_enum)
        mock_get_user_domain.assert_called_once_with(self.conn, mock_domain_enum)

        self.assertEqual(res, {"domain_id": "default-domain-id"})

    @parameterized.expand(
        [
            ("with server side filters", {"arg1": "val1", "arg2": "val2"}),
            ("with no server side filters", None),
        ]
    )
    @patch("openstack_query.runners.user_runner.UserRunner._run_paginated_query")
    def test_run_query_with_meta_arg_domain_id(
        self, _, mock_filter_kwargs, mock_run_paginated_query
    ):
        """
        Tests the _run_query method works expectedly - when meta arg domain id given
        method should:
            - update filter kwargs to include "domain_id": <domain id given>
            - run _run_paginated_query with updated filter_kwargs
        """

        mock_user_list = mock_run_paginated_query.return_value = [
            "user1",
            "user2",
            "user3",
        ]
        mock_domain_id = "domain-id1"
        res = self.instance._run_query(
            self.conn, filter_kwargs=mock_filter_kwargs, domain_id=mock_domain_id
        )

        self.assertEqual(res, mock_user_list)

        if mock_filter_kwargs:
            mock_run_paginated_query.assert_called_once_with(
                self.conn.identity.users,
                {**{"domain_id": mock_domain_id}, **mock_filter_kwargs},
            )
        else:
            mock_run_paginated_query.assert_called_once_with(
                self.conn.identity.users, {"domain_id": mock_domain_id}
            )
        self.assertEqual(res, mock_user_list)

    @raises(ParseQueryError)
    def test_run_query_domain_id_meta_arg_preset_duplication(self):
        """
        Tests that an error is raised when run_query is called with filter kwargs which contians domain_id and with meta
        params that also contains a domain id - i.e. there's a mismatch in which domain to search
        """
        self.instance._run_query(
            self.conn,
            filter_kwargs={"domain_id": "some-domain"},
            domain_id=["some-other-domain"],
        )

    @parameterized.expand(
        [
            ("with server side filters", {"arg1": "val1", "arg2": "val2"}),
            ("with no server side filters", None),
        ]
    )
    @patch("openstack_query.runners.user_runner.UserRunner._run_paginated_query")
    @patch("openstack_query.runners.user_runner.UserRunner._get_user_domain")
    def test_run_query_no_meta_args(
        self, _, mock_filter_kwargs, mock_get_user_domain, mock_run_paginated_query
    ):
        """
        Tests that run_query functions expectedly - when no meta args given
        method should use the default-domain-id
        """
        mock_run_paginated_query.side_effect = [["user1", "user2"]]
        mock_get_user_domain.return_value = "default-domain-id"

        res = self.instance._run_query(
            self.conn, filter_kwargs=mock_filter_kwargs, domain_id=None
        )

        if not mock_filter_kwargs:
            mock_filter_kwargs = {}

        mock_get_user_domain.assert_called_once_with(
            self.conn, self.instance.DEFAULT_DOMAIN
        )
        mock_run_paginated_query.asset_called_once_with(
            self.conn.identity.users,
            {
                **mock_filter_kwargs,
                **{"all_tenants": True, "domain_id": "default-domain-id"},
            },
        )

        self.assertEqual(res, ["user1", "user2"])

    @raises(ParseQueryError)
    def test_run_query_with_from_domain_and_id_given(self):
        """
        Test error is raised when the domain name and domain id is provided at
        the same time
        """
        self.instance._run_query(
            self.conn, filter_kwargs={"domain_id": 1}, domain_id="domain-id2"
        )

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
