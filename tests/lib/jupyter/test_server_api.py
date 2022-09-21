import unittest
from unittest.mock import patch, NonCallableMock, call

from nose.tools import assert_raises_regexp, raises

from jupyter_api.api_endpoints import API_ENDPOINTS
from jupyter_api.user_api import UserApi
from structs.jupyter_users import JupyterUsers


@patch("jupyter_api.user_api.httpx")
class UserApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.api = UserApi()

    def test_start_servers_single_user(self, httpx):
        """
        Tests that the start_servers method calls the correct endpoint
        """
        token = NonCallableMock()
        user_names = JupyterUsers(name="test", start_index=None, end_index=None)
        httpx.post.return_value.status_code = 201

        self.api.start_servers("dev", token, user_names)
        httpx.post.assert_called_once_with(
            url=API_ENDPOINTS["dev"] + "/hub/api/users/test/server",
            headers={"Authorization": f"token {token}"},
            timeout=60,
        )

    def test_start_servers_multiple_users(self, httpx):
        """
        Tests that the start_servers method calls the correct endpoint
        and usernames
        """
        token = NonCallableMock()
        start_index, end_index = 1, 10
        user_names = JupyterUsers(
            name="test", start_index=start_index, end_index=end_index
        )
        httpx.post.return_value.status_code = 201

        self.api.start_servers("dev", token, user_names)
        for i, user_index in enumerate(range(start_index, end_index + 1)):
            assert httpx.post.call_args_list[i] == call(
                url=API_ENDPOINTS["dev"] + f"/hub/api/users/test-{user_index}/server",
                headers={"Authorization": f"token {token}"},
                timeout=60,
            )
        assert httpx.post.call_count == (end_index - start_index + 1)

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

    def test_start_servers_incorrect_order(self, _):
        """
        Tests that the start_servers method raises an error if the end_index is greater than start
        """
        user_names = JupyterUsers(name="test", start_index=2, end_index=1)
        with assert_raises_regexp(RuntimeError, "must be less than"):
            self.api.start_servers("dev", "token", user_names)

    def test_start_servers_handles_error(self, httpx):
        """
        Tests that the start_servers method logs an error if the request fails
        """
        token = NonCallableMock()
        user_names = JupyterUsers(name="test", start_index=None, end_index=None)
        httpx.post.return_value.status_code = 500

        with self.assertRaisesRegex(RuntimeError, "Failed to request server"):
            self.api.start_servers("dev", token, user_names)

    def test_stop_servers_single_user(self, httpx):
        """
        Tests that the stop_servers method calls the correct endpoint
        """
        token = NonCallableMock()
        user_names = JupyterUsers(name="test", start_index=None, end_index=None)
        async_client = httpx.AsyncClient.return_value.__aenter__.return_value

        self.api.stop_servers("dev", token, user_names)
        async_client.delete.assert_called_once_with(
            url=API_ENDPOINTS["dev"] + "/hub/api/users/test/server",
            headers={"Authorization": f"token {token}"},
            timeout=60,
        )

    def test_stop_servers_multiple_users(self, httpx):
        """
        Tests that the stop_servers method calls the correct endpoint
        and usernames
        """
        token = NonCallableMock()
        start_index, end_index = 1, 10
        user_names = JupyterUsers(
            name="test", start_index=start_index, end_index=end_index
        )
        async_client = httpx.AsyncClient.return_value.__aenter__.return_value

        self.api.stop_servers("dev", token, user_names)
        for i, user_index in enumerate(range(start_index, end_index + 1)):
            assert async_client.delete.call_args_list[i] == call(
                url=API_ENDPOINTS["dev"] + f"/hub/api/users/test-{user_index}/server",
                headers={"Authorization": f"token {token}"},
                timeout=60,
            )
        assert async_client.delete.call_count == (end_index - start_index + 1)

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

    def test_stop_servers_incorrect_order(self, _):
        """
        Tests that the stop_servers method raises an error if the end_index is greater than start
        """
        user_names = JupyterUsers(name="test", start_index=2, end_index=1)
        with assert_raises_regexp(RuntimeError, "must be less than"):
            self.api.stop_servers("dev", "token", user_names)
