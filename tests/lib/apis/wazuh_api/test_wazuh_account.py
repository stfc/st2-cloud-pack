from typing import List, Dict
import pytest
from apis.wazuh_api.structs.wazuh_account import WazuhAccount


@pytest.fixture(name="mock_wazuh_accounts")
def mock_wazuh_accounts_fixture() -> List[Dict]:
    """
    Fixture which contains a test wazuh account in a dict
    """
    return [
        {
            "name": "config1",
            "username": "wazuh",
            "password": "pass",
            "wazuh_endpoint": "wazuh.test.com",
        }
    ]


@pytest.fixture(name="mock_pack_config")
def mock_pack_config_fixture(mock_wazuh_accounts):
    """Fixture sets up a mock pack config to test with"""
    return {"wazuh_accounts": mock_wazuh_accounts}


def test_from_dict():
    """
    Tests that from_dict() static method works properly
    this method should build a WazuhAccount dataclass from a valid dictionary
    """
    mock_valid_kwargs = {
        "username": "user1",
        "password": "some-pass",
        "wazuh_endpoint": "sever",
    }
    mock_invalid_kwargs = {"to_ignore1": "val1", "to_ignore2": "val2"}

    res = WazuhAccount.from_dict({**mock_valid_kwargs, **mock_invalid_kwargs})
    for key, val in mock_valid_kwargs.items():
        assert val == getattr(res, key)


def test_from_pack_config_valid(mock_wazuh_accounts, mock_pack_config):
    """
    Tests that from_pack_config() static method works properly
    this method should build a WazuhAccount dataclass from a valid
    stackstorm pack_config and a wazuh_account_name
    """
    for mock_accounts in mock_wazuh_accounts:
        expected_attrs = dict(mock_accounts)
        expected_attrs.pop("name")

        res = WazuhAccount.from_pack_config(mock_pack_config, "config1")
        for key, val in expected_attrs.items():
            assert val == getattr(res, key)


def test_from_pack_config_invalid_name(mock_pack_config):
    """
    Tests that from_pack_config() method works properly - when given an invalid wazuh_account_name
    should raise an error if pack config does not contain entry matching wazuh_account_name
    """
    with pytest.raises(KeyError):
        WazuhAccount.from_pack_config(mock_pack_config, "invalid-config")


def test_from_pack_config_invalid_pack():
    """
    Tests that from_pack_config() method works properly - when given an invalid pack_config
    should raise an error if pack config could not be found
    """
    with pytest.raises(ValueError):
        WazuhAccount.from_pack_config({}, "config1")
