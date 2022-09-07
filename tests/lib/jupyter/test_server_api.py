import unittest
from unittest.mock import patch, NonCallableMock, call

from nose.tools import raises

from jupyter_api.api_endpoints import API_ENDPOINTS
from jupyter_api.user_api import UserApi
from structs.jupyter_users import JupyterUsers


@patch("jupyter_api.user_api.requests")
class UserApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.api = UserApi()

    def test_start_servers_single_user(self, requests):
        """
        Tests that the start_servers method calls the correct endpoint
        """
        token = NonCallableMock()
        user_names = JupyterUsers(name="test", start_index=None, end_index=None)
        requests.post.return_value.status_code = 201

        self.api.start_servers("dev", token, user_names)
        requests.post.assert_called_once_with(
            url=API_ENDPOINTS["dev"] + "/hub/api/users/test/server",
            headers={"Authorization": f"token {token}"},
            timeout=60,
        )

    def test_start_servers_multiple_users(self, requests):
        """
        Tests that the start_servers method calls the correct endpoint
        and usernames
        """
        token = NonCallableMock()
        start_index, end_index = 1, 10
        user_names = JupyterUsers(
            name="test", start_index=start_index, end_index=end_index
        )
        requests.post.return_value.status_code = 201

        self.api.start_servers("dev", token, user_names)
        for i, user_index in enumerate(range(start_index, end_index + 1)):
            assert requests.post.call_args_list[i] == call(
                url=API_ENDPOINTS["dev"] + f"/hub/api/users/test-{user_index}/server",
                headers={"Authorization": f"token {token}"},
                timeout=60,
            )
        assert requests.post.call_count == (end_index - start_index + 1)

    @raises(RuntimeError)
    def test_start_servers_missing_start_index(self, _):
        """
        Tests that the start_servers method raises an error if the start_index is not provided
        """
        user_names = JupyterUsers(name="test", start_index=None, end_index=1)
        self.api.start_servers("dev", "token", user_names)

    @raises(RuntimeError)
    def test_start_servers_missing_end_index(self, _):
        """
        Tests that the start_servers method raises an error if the end_index is not provided
        """
        user_names = JupyterUsers(name="test", start_index=1, end_index=None)
        self.api.start_servers("dev", "token", user_names)

    @raises(RuntimeError)
    def test_start_servers_incorrect_order(self, _):
        """
        Tests that the start_servers method raises an error if the start_index is not provided
        """
        user_names = JupyterUsers(name="test", start_index=1, end_index=2)
        self.api.start_servers("dev", "token", user_names)

    def test_stop_servers_single_user(self, requests):
        """
        Tests that the stop_servers method calls the correct endpoint
        """
        token = NonCallableMock()
        user_names = JupyterUsers(name="test", start_index=None, end_index=None)
        requests.delete.return_value.status_code = 204

        self.api.stop_servers("dev", token, user_names)
        requests.delete.assert_called_once_with(
            url=API_ENDPOINTS["dev"] + "/hub/api/users/test/server",
            headers={"Authorization": f"token {token}"},
            timeout=60,
        )

    def test_stop_servers_multiple_users(self, requests):
        """
        Tests that the stop_servers method calls the correct endpoint
        and usernames
        """
        token = NonCallableMock()
        start_index, end_index = 1, 10
        user_names = JupyterUsers(
            name="test", start_index=start_index, end_index=end_index
        )
        requests.delete.return_value.status_code = 204

        self.api.stop_servers("dev", token, user_names)
        for i, user_index in enumerate(range(start_index, end_index + 1)):
            assert requests.delete.call_args_list[i] == call(
                url=API_ENDPOINTS["dev"] + f"/hub/api/users/test-{user_index}/server",
                headers={"Authorization": f"token {token}"},
                timeout=60,
            )
        assert requests.delete.call_count == (end_index - start_index + 1)

    @raises(RuntimeError)
    def test_stop_servers_missing_start_index(self, _):
        """
        Tests that the stop_servers method raises an error if the start_index is not provided
        """
        user_names = JupyterUsers(name="test", start_index=None, end_index=1)
        self.api.stop_servers("dev", "token", user_names)

    @raises(RuntimeError)
    def test_stop_servers_missing_end_index(self, _):
        """
        Tests that the stop_servers method raises an error if the end_index is not provided
        """
        user_names = JupyterUsers(name="test", start_index=1, end_index=None)
        self.api.stop_servers("dev", "token", user_names)

    @raises(RuntimeError)
    def test_stop_servers_incorrect_order(self, _):
        """
        Tests that the stop_servers method raises an error if the start_index is not provided
        """
        user_names = JupyterUsers(name="test", start_index=1, end_index=2)
        self.api.stop_servers("dev", "token", user_names)
