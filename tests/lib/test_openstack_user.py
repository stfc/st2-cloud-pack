import unittest
from unittest.mock import MagicMock, patch

from openstack_api.openstack_user import OpenstackUser


class OpenstackuserTests(unittest.TestCase):
    """
    Runs various tests to ensure we are using the Openstack
    user module in the expected way
    """

    # pylint:disable=too-few-public-methods,invalid-name
    class MockProject:
        def __init__(self):
            self.id = "ProjectID"

        def __getitem__(self, item):
            return getattr(self, item)

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()
        with patch("openstack_api.openstack_user.OpenstackIdentity") as identity_mock:
            self.instance = OpenstackUser(self.mocked_connection)
            self.identity_module = identity_mock.return_value

        self.api = self.mocked_connection.return_value.__enter__.return_value

        self.mock_user_list = [
            {
                "id": "userid1",
                "name": "username1",
            },
            {
                "id": "userid2",
                "name": "username2",
            },
            {
                "id": "userid3",
                "name": "username3",
            },
        ]

    def test_search_all_users(self):
        """
        Tests calling search_all_users
        """
        self.instance.search_all_users(cloud_account="test", user_domain="domain")

        self.mocked_connection.assert_called_once_with("test")

        self.api.list_users.assert_called_once_with(
            domain_id="domain",
        )

    def test_search_users_name_in(self):
        """
        Tests calling search_users_name_in
        """

        self.instance.search_all_users = MagicMock()
        self.instance.search_all_users.return_value = self.mock_user_list

        result = self.instance.search_users_name_in(
            cloud_account="test",
            user_domain="domain",
            names=["username1", "username2"],
        )

        self.assertEqual(result, [self.mock_user_list[0], self.mock_user_list[1]])

    def test_search_users_name_not_in(self):
        """
        Tests calling search_users_name_not_in
        """

        self.instance.search_all_users = MagicMock()
        self.instance.search_all_users.return_value = self.mock_user_list

        result = self.instance.search_users_name_not_in(
            cloud_account="test",
            user_domain="domain",
            names=["username1", "username2"],
        )

        self.assertEqual(result, [self.mock_user_list[2]])

    def test_search_users_name_contains(self):
        """
        Tests calling search_users_name_contains
        """

        self.instance.search_all_users = MagicMock()
        self.instance.search_all_users.return_value = self.mock_user_list

        result = self.instance.search_users_name_contains(
            cloud_account="test",
            user_domain="domain",
            name_snippets=["user", "name2"],
        )

        self.assertEqual(result, [self.mock_user_list[1]])

        result = self.instance.search_users_name_contains(
            cloud_account="test", user_domain="domain", name_snippets=["name3"]
        )

        self.assertEqual(result, [self.mock_user_list[2]])

        result = self.instance.search_users_name_contains(
            cloud_account="test", user_domain="domain", name_snippets=["username"]
        )

        self.assertEqual(result, self.mock_user_list)

    def test_search_users_name_not_contains(self):
        """
        Tests calling search_users_name_not_contains
        """

        self.instance.search_all_users = MagicMock()
        self.instance.search_all_users.return_value = self.mock_user_list

        result = self.instance.search_users_name_not_contains(
            cloud_account="test",
            user_domain="domain",
            name_snippets=["user", "name"],
        )

        self.assertEqual(result, [])

        result = self.instance.search_users_name_not_contains(
            cloud_account="test", user_domain="domain", name_snippets=["name3"]
        )

        self.assertEqual(result, [self.mock_user_list[0], self.mock_user_list[1]])

        result = self.instance.search_users_name_not_contains(
            cloud_account="test", user_domain="domain", name_snippets=["username"]
        )

        self.assertEqual(result, [])

    def test_search_user_id_in(self):
        """
        Tests calling search_users_id_in
        """

        self.instance.search_all_users = MagicMock()
        self.instance.search_all_users.return_value = self.mock_user_list

        result = self.instance.search_users_id_in(
            cloud_account="test", user_domain="domain", ids=["userid1", "userid2"]
        )

        self.assertEqual(result, [self.mock_user_list[0], self.mock_user_list[1]])

    def test_search_users_id_not_in(self):
        """
        Tests calling search_users_id_not_in
        """

        self.instance.search_all_users = MagicMock()
        self.instance.search_all_users.return_value = self.mock_user_list

        result = self.instance.search_users_id_not_in(
            cloud_account="test", user_domain="domain", ids=["userid1", "userid2"]
        )

        self.assertEqual(result, [self.mock_user_list[2]])
