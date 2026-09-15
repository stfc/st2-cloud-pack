from typing import List, Dict
import pytest
from apis.netbox_api.structs.netbox_account import NetboxAccount


@pytest.fixture(name="mock_netbox_accounts")
def mock_netbox_accounts_fixture() -> List[Dict]:
    """
    Fixture which contains several test jira accounts in a dict
    """
    return [
        {
            "name": "config1",
            "api_token": "some-token",
            "netbox_endpoint": "https://netbox.example.com",
        }
    ]


@pytest.fixture(name="mock_pack_config")
def mock_pack_config_fixture(mock_netbox_accounts):
    """Fixture sets up a mock pack config to test with"""
    return {"netbox_accounts": mock_netbox_accounts}


def test_from_dict():
    """
    Tests that from_dict() static method works properly
    this method should build a NetboxAccount dataclass from a valid dictionary
    """

    mock_valid_kwargs = {
        "api_token": "some-pass2",
        "netbox_endpoint": "https://another-netbox.example.com",
    }
    mock_invalid_kwargs = {"to_ignore1": "val1", "to_ignore2": "val2"}

    res = NetboxAccount.from_dict({**mock_valid_kwargs, **mock_invalid_kwargs})
    for key, val in mock_valid_kwargs.items():
        assert val == getattr(res, key)


def test_from_pack_config_valid(mock_netbox_accounts, mock_pack_config):
    """
    Tests that from_pack_config() static method works properly
    this method should build a NetboxAccount dataclass from a valid
    stackstorm pack_config and an netbox_account_name
    """
    expected_attrs = dict(mock_netbox_accounts[0])
    expected_attrs.pop("name")

    res = NetboxAccount.from_pack_config(mock_pack_config, "config1")
    for key, val in expected_attrs.items():
        assert val == getattr(res, key)


def test_from_pack_config_invalid_name(mock_pack_config):
    """
    Tests that from_pack_config() method works properly - when given an invalid netbox_account_name
    should raise an error if pack config does not contain entry matching netbox_account_name
    """
    with pytest.raises(KeyError):
        NetboxAccount.from_pack_config(mock_pack_config, "invalid-config")


def test_from_pack_config_invalid_pack():
    """
    Tests that from_pack_config() method works properly - when given an invalid pack_config
    should raise an error if pack config could not be found
    """
    with pytest.raises(ValueError):
        NetboxAccount.from_pack_config({}, "config1")
