import unittest
from datetime import datetime
from unittest.mock import patch, NonCallableMock, Mock, call

import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta
from nose.tools import assert_raises_regexp, raises
from parameterized import parameterized

from jupyter_api.api_endpoints import API_ENDPOINTS
from jupyter_api.user_api import UserApi
from structs.jupyter_users import JupyterUsers


@patch("jupyter_api.user_api.requests")
class UserApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.api = UserApi()

    @parameterized.expand(["dev", "prod"])
    def test_get_users(self, requests, endpoint):
        """
        Tests that the get_users method calls the correct endpoint
        and serialises the JSON correctly
        """
        token = NonCallableMock()
        expected_name = "test"
        expected_time = "2020-01-01T00:00:00Z"

        requests.get.return_value.status_code = 200
        requests.get.return_value.json.return_value = [
            {"name": expected_name, "last_activity": expected_time}
        ]

        returned = self.api.get_users(endpoint, token)

        requests.get.assert_called_once_with(
            url=API_ENDPOINTS[endpoint] + "/hub/api/users",
            headers={"Authorization": f"token {token}"},
            timeout=300,
        )
        assert len(returned) == 1
        assert returned[0][0] == expected_name
        assert returned[0][1] == parser.parse(expected_time)

    @parameterized.expand(["dev", "prod"])
    def test_get_users_no_users(self, requests, endpoint):
        """
        Tests that the get_users method returns an empty list if no users are found
        """
        token = NonCallableMock()

        requests.get.return_value.status_code = 204
        requests.get.return_value.json.return_value = []

        returned = self.api.get_users(endpoint, token)

        requests.get.assert_called_once_with(
            url=API_ENDPOINTS[endpoint] + "/hub/api/users",
            headers={"Authorization": f"token {token}"},
            timeout=300,
        )
        assert len(returned) == 0

    def test_get_users_handles_error(self, requests):
        """
        Tests that the get_users method logs an error if the request fails
        """
        requests.get.return_value.status_code = 500
        requests.get.return_value.json.return_value = []

        with self.assertRaisesRegex(RuntimeError, "Failed to get users"):
            self.api.get_users("dev", "token")

    def test_get_inactive_users(self, _):
        """
        Tests the get_inactive_users filters out active users
        correctly
        """
        # Patch get_users to return a list of users
        threshold = relativedelta(seconds=1)
        active_user = ("test", pytz.utc.localize(datetime.now()))
        inactive_user = (
            "test2",
            pytz.utc.localize(datetime.now() - relativedelta(seconds=2)),
        )

        self.api.get_users = Mock(return_value=[active_user, inactive_user])
        returned = self.api.get_inactive_users("dev", "token", threshold)

        self.api.get_users.assert_called_once_with("dev", "token")

        assert len(returned) == 1
        assert returned[0] == inactive_user

    def test_get_inactive_users_no_users(self, _):
        """
        Tests the get_inactive_users method returns an empty list if no users are found
        """
        self.api.get_users = Mock(return_value=[])
        returned = self.api.get_inactive_users("dev", "token", relativedelta(seconds=1))

        self.api.get_users.assert_called_once_with("dev", "token")
        assert not returned

    def test_remove_users_single_user(self, requests):
        """
        Tests that the delete_users method calls the correct endpoint
        """
        token = NonCallableMock()
        user_names = JupyterUsers(name="test", start_index=None, end_index=None)
        requests.delete.return_value.status_code = 204

        self.api.delete_users("dev", token, user_names)
        requests.delete.assert_called_once_with(
            url=API_ENDPOINTS["dev"] + "/hub/api/users/test",
            headers={"Authorization": f"token {token}"},
            timeout=300,
        )

    def test_remove_users_multiple_users(self, requests):
        """
        Tests that the delete_users method calls the correct endpoint
        and usernames
        """
        token = NonCallableMock()
        start_index, end_index = 1, 10
        user_names = JupyterUsers(
            name="test", start_index=start_index, end_index=end_index
        )
        requests.delete.return_value.status_code = 204

        self.api.delete_users("dev", token, user_names)
        for i, user_index in enumerate(range(start_index, end_index + 1)):
            assert requests.delete.call_args_list[i] == call(
                url=API_ENDPOINTS["dev"] + f"/hub/api/users/test-{user_index}",
                headers={"Authorization": f"token {token}"},
                timeout=300,
            )
        assert requests.delete.call_count == (end_index - start_index + 1)

    @raises(RuntimeError)
    def test_remove_users_missing_start_index(self, _):
        """
        Tests that the delete_users method raises an error if the start_index is not provided
        """
        user_names = JupyterUsers(name="test", start_index=None, end_index=1)
        self.api.delete_users("dev", "token", user_names)

    @raises(RuntimeError)
    def test_remove_users_missing_end_index(self, _):
        """
        Tests that the delete_users method raises an error if the end_index is not provided
        """
        user_names = JupyterUsers(name="test", start_index=1, end_index=None)
        self.api.delete_users("dev", "token", user_names)

    def test_remove_users_incorrect_order(self, _):
        """
        Tests that the delete_users method raises an error if the end_index is greater than start
        """
        user_names = JupyterUsers(name="test", start_index=2, end_index=1)
        with assert_raises_regexp(RuntimeError, "must be less than"):
            self.api.delete_users("dev", "token", user_names)
