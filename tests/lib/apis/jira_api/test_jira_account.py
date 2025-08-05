from typing import List, Dict
import pytest
from apis.jira_api.structs.jira_account import JiraAccount


@pytest.fixture(name="mock_jira_accounts")
def mock_jira_accounts_fixture() -> List[Dict]:
    """
    Fixture which contains several test jira accounts in a dict
    """
    return [
        {
            "name": "config1",
            "username": "user1",
            "api_token": "some-pass",
            "atlassian_endpoint": "sever",
        }
    ]


@pytest.fixture(name="mock_pack_config")
def mock_pack_config_fixture(mock_jira_accounts):
    """Fixture sets up a mock pack config to test with"""
    return {"jira_accounts": mock_jira_accounts}


def test_from_dict():
    """
    Tests that from_dict() static method works properly
    this method should build a jiraAccount dataclass from a valid dictionary
    """

    mock_valid_kwargs = {
        "username": "user1",
        "api_token": "some-pass",
        "atlassian_endpoint": "sever",
    }
    mock_invalid_kwargs = {"to_ignore1": "val1", "to_ignore2": "val2"}

    res = JiraAccount.from_dict({**mock_valid_kwargs, **mock_invalid_kwargs})
    for key, val in mock_valid_kwargs.items():
        assert val == getattr(res, key)


def test_from_pack_config_valid(mock_jira_accounts, mock_pack_config):
    """
    Tests that from_pack_config() static method works properly
    this method should build a jiraAccount dataclass from a valid
    stackstorm pack_config and an jira_account_name
    """
    expected_attrs = dict(mock_jira_accounts[0])
    expected_attrs.pop("name")

    res = JiraAccount.from_pack_config(mock_pack_config, "config1")
    for key, val in expected_attrs.items():
        assert val == getattr(res, key)


def test_from_pack_config_invalid_name(mock_pack_config):
    """
    Tests that from_pack_config() method works properly - when given an invalid jira_account_name
    should raise an error if pack config does not contain entry matching jira_account_name
    """
    with pytest.raises(KeyError):
        JiraAccount.from_pack_config(mock_pack_config, "invalid-config")


def test_from_pack_config_invalid_pack():
    """
    Tests that from_pack_config() method works properly - when given an invalid pack_config
    should raise an error if pack config could not be found
    """
    with pytest.raises(ValueError):
        JiraAccount.from_pack_config({}, "config1")
