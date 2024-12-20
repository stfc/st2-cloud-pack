from unittest.mock import patch, NonCallableMock, call
import pytest


from jupyter_api.api_endpoints import API_ENDPOINTS
from jupyter_api.user_api import UserApi
from structs.jupyter_users import JupyterUsers


@pytest.fixture(name="api_instance")
def api_instance_fixture() -> None:
    """
    Creates a new instance of the API class for each test
    """
    return UserApi()


@patch("jupyter_api.user_api.requests")
def test_start_servers_single_user(requests, api_instance):
    """
    Tests that the start_servers method calls the correct endpoint
    """
    token = NonCallableMock()
    user_names = JupyterUsers(name="test", start_index=None, end_index=None)
    requests.post.return_value.status_code = 201

    api_instance.start_servers("dev", token, user_names)
    requests.post.assert_called_once_with(
        url=API_ENDPOINTS["dev"] + "/hub/api/users/test/server",
        headers={"Authorization": f"token {token}"},
        timeout=60,
    )


@patch("jupyter_api.user_api.requests")
def test_start_servers_multiple_users(requests, api_instance):
    """
    Tests that the start_servers method calls the correct endpoint
    and usernames
    """
    token = NonCallableMock()
    start_index, end_index = 1, 10
    user_names = JupyterUsers(name="test", start_index=start_index, end_index=end_index)
    requests.post.return_value.status_code = 201

    api_instance.start_servers("dev", token, user_names)
    for i, user_index in enumerate(range(start_index, end_index + 1)):
        assert requests.post.call_args_list[i] == call(
            url=API_ENDPOINTS["dev"] + f"/hub/api/users/test-{user_index}/server",
            headers={"Authorization": f"token {token}"},
            timeout=60,
        )
    assert requests.post.call_count == (end_index - start_index + 1)


def test_start_servers_missing_start_index(api_instance):
    """
    Tests that the start_servers method raises an error if the start_index is not provided
    """
    user_names = JupyterUsers(name="test", start_index=None, end_index=1)
    with pytest.raises(RuntimeError):
        api_instance.start_servers("dev", "token", user_names)


def test_start_servers_missing_end_index(api_instance):
    """
    Tests that the start_servers method raises an error if the end_index is not provided
    """
    user_names = JupyterUsers(name="test", start_index=1, end_index=None)
    with pytest.raises(RuntimeError):
        api_instance.start_servers("dev", "token", user_names)


def test_start_servers_incorrect_order(api_instance):
    """
    Tests that the start_servers method raises an error if the end_index is greater than start
    """
    user_names = JupyterUsers(name="test", start_index=2, end_index=1)
    with pytest.raises(RuntimeError, match="must be less than"):
        api_instance.start_servers("dev", "token", user_names)


@patch("jupyter_api.user_api.requests")
def test_start_servers_handles_error(requests, api_instance):
    """
    Tests that the start_servers method logs an error if the request fails
    """
    token = NonCallableMock()
    user_names = JupyterUsers(name="test", start_index=None, end_index=None)
    requests.post.return_value.status_code = 500

    with pytest.raises(RuntimeError, match="Failed to request server"):
        api_instance.start_servers("dev", token, user_names)


@patch("jupyter_api.user_api.requests")
def test_stop_servers_single_user(requests, api_instance):
    """
    Tests that the stop_servers method calls the correct endpoint
    """
    token = NonCallableMock()
    user_names = JupyterUsers(name="test", start_index=None, end_index=None)
    requests.delete.return_value.status_code = 204

    api_instance.stop_servers("dev", token, user_names)
    requests.delete.assert_called_once_with(
        url=API_ENDPOINTS["dev"] + "/hub/api/users/test/server",
        headers={"Authorization": f"token {token}"},
        timeout=60,
    )


@patch("jupyter_api.user_api.requests")
def test_stop_servers_multiple_users(requests, api_instance):
    """
    Tests that the stop_servers method calls the correct endpoint
    and usernames
    """
    token = NonCallableMock()
    start_index, end_index = 1, 10
    user_names = JupyterUsers(name="test", start_index=start_index, end_index=end_index)
    requests.delete.return_value.status_code = 204

    api_instance.stop_servers("dev", token, user_names)
    for i, user_index in enumerate(range(start_index, end_index + 1)):
        assert requests.delete.call_args_list[i] == call(
            url=API_ENDPOINTS["dev"] + f"/hub/api/users/test-{user_index}/server",
            headers={"Authorization": f"token {token}"},
            timeout=60,
        )
    assert requests.delete.call_count == (end_index - start_index + 1)


def test_stop_servers_missing_start_index(api_instance):
    """
    Tests that the stop_servers method raises an error if the start_index is not provided
    """
    user_names = JupyterUsers(name="test", start_index=None, end_index=1)
    with pytest.raises(RuntimeError):
        api_instance.stop_servers("dev", "token", user_names)


def test_stop_servers_missing_end_index(api_instance):
    """
    Tests that the stop_servers method raises an error if the end_index is not provided
    """
    user_names = JupyterUsers(name="test", start_index=1, end_index=None)
    with pytest.raises(RuntimeError):
        api_instance.stop_servers("dev", "token", user_names)


def test_stop_servers_incorrect_order(api_instance):
    """
    Tests that the stop_servers method raises an error if the end_index is greater than start
    """
    user_names = JupyterUsers(name="test", start_index=2, end_index=1)
    with pytest.raises(RuntimeError, match="must be less than"):
        api_instance.stop_servers("dev", "token", user_names)


@patch("jupyter_api.user_api.requests")
def test_stop_servers_handles_error(requests, api_instance):
    """
    Tests that the stop_servers method logs an error if the request fails
    """
    token = NonCallableMock()
    user_names = JupyterUsers(name="test", start_index=None, end_index=None)
    requests.delete.return_value.status_code = 500

    with pytest.raises(RuntimeError, match="Failed to stop server"):
        api_instance.stop_servers("dev", token, user_names)
