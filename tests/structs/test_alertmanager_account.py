from typing import List, Dict
import pytest
from requests.auth import HTTPBasicAuth

from structs.alertmanager.alertmanager_account import AlertManagerAccount


@pytest.fixture(name="mock_alertmanager_account")
def mock_alertmanager_accounts_fixture() -> List[Dict]:
    """
    Fixture which contains several test alertmanager accounts in a dict
    """
    return [
        {
            "name": "config1",
            "username": "user1",
            "password": "some-pass",
            "alertmanager_endpoint": "prod",
        }
    ]


@pytest.fixture(name="mock_pack_config")
def mock_pack_config_fixture(mock_alertmanager_account):
    """Fixture sets up a mock pack config to test with"""
    return {"alertmanager_accounts": mock_alertmanager_account}


def test_from_dict():
    """
    Tests that from_dict() static method works properly
    this method should build a IcingaAccount dataclass from a valid dictionary
    """

    mock_valid_kwargs = {
        "username": "user1",
        "password": "some-pass",
        "alertmanager_endpoint": "sever",
    }
    mock_invalid_kwargs = {"to_ignore1": "val1", "to_ignore2": "val2"}

    res = AlertManagerAccount.from_dict({**mock_valid_kwargs, **mock_invalid_kwargs})
    for key, val in mock_valid_kwargs.items():
        assert val == getattr(res, key)


def test_am_from_pack_config_valid(mock_alertmanager_account, mock_pack_config):
    """
    Tests that from_pack_config() static method works properly
    this method should build a AlertManager dataclass from a valid
    stackstorm pack_config and an alertmanager_account
    """
    expected_attrs = dict(mock_alertmanager_account[0])
    expected_attrs.pop("name")

    res = AlertManagerAccount.from_pack_config(mock_pack_config, "config1")
    for key, val in expected_attrs.items():
        assert val == getattr(res, key)


def test_am_from_pack_config_invalid_name(mock_pack_config):
    """
    Tests that from_pack_config() method works properly - when given an invalid alertmanager_account_name
    should raise an error if pack config does not contain entry matching alertmanager_account_name
    """
    with pytest.raises(KeyError):
        AlertManagerAccount.from_pack_config(mock_pack_config, "invalid-config")


def test_am_from_pack_config_invalid_pack():
    """
    Tests that from_pack_config() method works properly - when given an invalid pack_config
    should raise an error if pack config could not be found
    """
    with pytest.raises(ValueError):
        AlertManagerAccount.from_pack_config({}, "config1")


def test_am_auth_property():
    account = AlertManagerAccount(
        username="user1", password="some-pass", alertmanager_endpoint="foo"
    )
    assert account.auth == HTTPBasicAuth(username="user1", password="some-pass")
