import unittest
from unittest.mock import MagicMock, patch, NonCallableMock

from nose.tools import raises

from exceptions.parse_query_error import ParseQueryError
from openstack_query.managers.user_manager import UserManager


# pylint:disable=protected-access,


class QueryManagerTests(unittest.TestCase):
    """
    Runs various tests to ensure that QueryManager class methods function expectedly
    """

    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()

        self.query = MagicMock()
        self.prop_cls = MagicMock()
        self.instance = UserManager(cloud_account="test_account")

    @raises(ParseQueryError)
    def test_search_datetime_raise_error(self):
        """
        Test that ParseQueryError is raised when someone tries to query
        using datetime
        """
        mock_kwargs = {
            "search_mode": "younger_than",
            "property_to_search_by": "mock_prop",
            "date 1": "2023-08-01",
        }
        self.instance.search_by_datetime(**mock_kwargs)
