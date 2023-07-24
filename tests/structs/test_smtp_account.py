import unittest
from nose.tools import raises
from structs.smtp_account import SMTPAccount


class TestEmailParams(unittest.TestCase):
    """
    Tests that methods in EmailParams dataclass work expectedly
    """

    def setUp(self) -> None:
        self.mock_smtp_accounts_config = [
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
        self.mock_pack_config = {"smtp_accounts": self.mock_smtp_accounts_config}

    def test_from_dict(self):
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
            self.assertEqual(val, getattr(res, key))

    def test_from_pack_config_valid(self):
        expected_attrs = {**self.mock_smtp_accounts_config[0]}
        expected_attrs.pop("name")

        res = SMTPAccount.from_pack_config(self.mock_pack_config, "config1")
        for key, val in expected_attrs.items():
            self.assertEqual(val, getattr(res, key))

    @raises(KeyError)
    def test_from_pack_config_invalid_name(self):
        SMTPAccount.from_pack_config(self.mock_pack_config, "invalid-config")

    @raises(ValueError)
    def test_from_pack_config_invalid_pack(self):
        SMTPAccount.from_pack_config({}, "config1")
