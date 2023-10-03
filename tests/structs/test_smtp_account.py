from typing import List, Dict
import pytest
from structs.email.smtp_account import SMTPAccount


@pytest.fixture(name="mock_smtp_accounts")
def mock_smtp_accounts_fixture() -> List[Dict]:
    """
    Fixture which contains several test smtp accounts in a dict
    """
    return [
        {
            "name": "config1",
            "username": "user1",
            "password": "some-pass",
            "server": "sever",
            "port": "port",
            "secure": True,
            "smtp_auth": True,
        },
        {
            "name": "config2",
            "username": "user2",
            "password": "some-pass2",
            "server": "sever",
            "port": "port",
            "secure": False,
            "smtp_auth": False,
        },
    ]


@pytest.fixture(name="mock_pack_config")
def mock_pack_config_fixture(mock_smtp_accounts):
    """Fixture sets up a mock pack config to test with"""
    return {"smtp_accounts": mock_smtp_accounts}


def test_from_dict():
    """
    Tests that from_dict() static method works properly
    this method should build a SMTPAccount dataclass from a valid dictionary
    """

    mock_valid_kwargs = {
        "username": "user1",
        "password": "some-pass",
        "server": "sever",
        "port": "port",
        "secure": True,
        "smtp_auth": True,
    }
    mock_invalid_kwargs = {"to_ignore1": "val1", "to_ignore2": "val2"}

    res = SMTPAccount.from_dict({**mock_valid_kwargs, **mock_invalid_kwargs})
    for key, val in mock_valid_kwargs.items():
        assert val == getattr(res, key)


def test_from_pack_config_valid(mock_smtp_accounts, mock_pack_config):
    """
    Tests that from_pack_config() static method works properly
    this method should build a SMTPAccount dataclass from a valid
    stackstorm pack_config and an smtp_account_name
    """
    expected_attrs = dict(mock_smtp_accounts[0])
    expected_attrs.pop("name")

    res = SMTPAccount.from_pack_config(mock_pack_config, "config1")
    for key, val in expected_attrs.items():
        assert val == getattr(res, key)


def test_from_pack_config_invalid_name(mock_pack_config):
    """
    Tests that from_pack_config() method works properly - when given an invalid smtp_account_name
    should raise an error if pack config does not contain entry matching smtp_account_name
    """
    with pytest.raises(KeyError):
        SMTPAccount.from_pack_config(mock_pack_config, "invalid-config")


def test_from_pack_config_invalid_pack():
    """
    Tests that from_pack_config() method works properly - when given an invalid pack_config
    should raise an error if pack config could not be found
    """
    with pytest.raises(ValueError):
        SMTPAccount.from_pack_config({}, "config1")
