from datetime import datetime
from unittest.mock import patch, NonCallableMock, Mock, call

import pytest
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta

from jupyter_api.api_endpoints import API_ENDPOINTS
from jupyter_api.user_api import UserApi
from structs.jupyter_users import JupyterUsers


@pytest.fixture(name="patch_requests", scope="function", autouse=True)
def patch_requests_fixture():
    """
    Returns a patched instance of the requests library, this is scoped
    for the duration of the test instance
    """
    with patch("jupyter_api.user_api.requests") as mock_patch_requests:
        yield mock_patch_requests


@pytest.fixture(name="api")
def api_fixture():
    """
    Returns a new instance of the UserApi class for each test
    """
    return UserApi()


@pytest.mark.parametrize("endpoint", ["dev", "prod"])
def test_get_users(endpoint, api, patch_requests):
    """
    Tests that the get_users method calls the correct endpoint
    and serialises the JSON correctly
    """
    token = NonCallableMock()
    expected_name = "test"
    expected_time = "2020-01-01T00:00:00Z"

    patch_requests.get.return_value.status_code = 200
    patch_requests.get.return_value.json.return_value = [
        {"name": expected_name, "last_activity": expected_time}
    ]

    returned = api.get_users(endpoint, token)

    patch_requests.get.assert_called_once_with(
        url=API_ENDPOINTS[endpoint] + "/hub/api/users",
        headers={"Authorization": f"token {token}"},
        timeout=300,
    )
    assert len(returned) == 1
    assert returned[0][0] == expected_name
    assert returned[0][1] == parser.parse(expected_time)


@pytest.mark.parametrize("endpoint", ["dev", "prod"])
def test_get_users_no_users(endpoint, api, patch_requests):
    """
    Tests that the get_users method returns an empty list if no users are found
    """
    token = NonCallableMock()

    patch_requests.get.return_value.status_code = 204
    patch_requests.get.return_value.json.return_value = []

    returned = api.get_users(endpoint, token)

    patch_requests.get.assert_called_once_with(
        url=API_ENDPOINTS[endpoint] + "/hub/api/users",
        headers={"Authorization": f"token {token}"},
        timeout=300,
    )
    assert len(returned) == 0


def test_get_users_handles_error(patch_requests, api):
    """
    Tests that the get_users method logs an error if the request fails
    """
    patch_requests.get.return_value.status_code = 500
    patch_requests.get.return_value.json.return_value = []

    with pytest.raises(RuntimeError, match="Failed to get users"):
        api.get_users("dev", "token")


def test_get_inactive_users(api):
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

    api.get_users = Mock(return_value=[active_user, inactive_user])
    returned = api.get_inactive_users("dev", "token", threshold)

    api.get_users.assert_called_once_with("dev", "token")

    assert len(returned) == 1
    assert returned[0] == inactive_user


def test_get_inactive_users_no_users(api):
    """
    Tests the get_inactive_users method returns an empty list if no users are found
    """
    api.get_users = Mock(return_value=[])
    returned = api.get_inactive_users("dev", "token", relativedelta(seconds=1))

    api.get_users.assert_called_once_with("dev", "token")
    assert not returned


def test_remove_users_single_user(patch_requests, api):
    """
    Tests that the delete_users method calls the correct endpoint
    """
    token = NonCallableMock()
    user_names = JupyterUsers(name="test", start_index=None, end_index=None)
    patch_requests.delete.return_value.status_code = 204

    api.delete_users("dev", token, user_names)
    patch_requests.delete.assert_called_once_with(
        url=API_ENDPOINTS["dev"] + "/hub/api/users/test",
        headers={"Authorization": f"token {token}"},
        timeout=300,
    )


def test_remove_users_multiple_users(patch_requests, api):
    """
    Tests that the delete_users method calls the correct endpoint
    and usernames
    """
    token = NonCallableMock()
    start_index, end_index = 1, 10
    user_names = JupyterUsers(name="test", start_index=start_index, end_index=end_index)
    patch_requests.delete.return_value.status_code = 204

    api.delete_users("dev", token, user_names)
    for i, user_index in enumerate(range(start_index, end_index + 1)):
        assert patch_requests.delete.call_args_list[i] == call(
            url=API_ENDPOINTS["dev"] + f"/hub/api/users/test-{user_index}",
            headers={"Authorization": f"token {token}"},
            timeout=300,
        )
    assert patch_requests.delete.call_count == (end_index - start_index + 1)


def test_remove_users_missing_start_index(api):
    """
    Tests that the delete_users method raises an error if the start_index is not provided
    """
    user_names = JupyterUsers(name="test", start_index=None, end_index=1)
    with pytest.raises(RuntimeError):
        api.delete_users("dev", "token", user_names)


def test_remove_users_missing_end_index(api):
    """
    Tests that the delete_users method raises an error if the end_index is not provided
    """
    user_names = JupyterUsers(name="test", start_index=1, end_index=None)
    with pytest.raises(RuntimeError):
        api.delete_users("dev", "token", user_names)


def test_remove_users_incorrect_order(api):
    """
    Tests that the delete_users method raises an error if the end_index is greater than start
    """
    user_names = JupyterUsers(name="test", start_index=2, end_index=1)
    with pytest.raises(RuntimeError, match="must be less than"):
        api.delete_users("dev", "token", user_names)


def test_create_users_single_user(patch_requests, api):
    """
    Tests that the create_users method calls the correct endpoint
    """
    token = NonCallableMock()
    user_names = JupyterUsers(name="test", start_index=None, end_index=None)
    patch_requests.post.return_value.status_code = 201

    api.create_users("dev", token, user_names)
    patch_requests.post.assert_called_once_with(
        url=API_ENDPOINTS["dev"] + "/hub/api/users/test",
        headers={"Authorization": f"token {token}"},
        timeout=60,
    )


def test_create_users_multiple_users(patch_requests, api):
    """
    Tests that the create_users method calls the correct endpoint
    and usernames
    """
    token = NonCallableMock()
    start_index, end_index = 1, 10
    user_names = JupyterUsers(name="test", start_index=start_index, end_index=end_index)
    patch_requests.post.return_value.status_code = 201

    api.create_users("dev", token, user_names)
    for i, user_index in enumerate(range(start_index, end_index + 1)):
        assert patch_requests.post.call_args_list[i] == call(
            url=API_ENDPOINTS["dev"] + f"/hub/api/users/test-{user_index}",
            headers={"Authorization": f"token {token}"},
            timeout=60,
        )
    assert patch_requests.post.call_count == (end_index - start_index + 1)


def test_create_users_missing_start_index(api):
    """
    Tests that the create_users method raises an error if the start_index is not provided
    """
    user_names = JupyterUsers(name="test", start_index=None, end_index=1)
    with pytest.raises(RuntimeError):
        api.create_users("dev", "token", user_names)


def test_create_users_missing_end_index(api):
    """
    Tests that the create_users method raises an error if the end_index is not provided
    """
    user_names = JupyterUsers(name="test", start_index=1, end_index=None)
    with pytest.raises(RuntimeError):
        api.create_users("dev", "token", user_names)


def test_create_users_incorrect_order(api):
    """
    Tests that the create_users method raises an error if the end_index is greater than start
    """
    user_names = JupyterUsers(name="test", start_index=2, end_index=1)
    with pytest.raises(RuntimeError, match="must be less than"):
        api.create_users("dev", "token", user_names)
