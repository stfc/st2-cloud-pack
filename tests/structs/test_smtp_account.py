import unittest

from structs.email.smtp_account import SMTPAccount


class TestEmailParams(unittest.TestCase):
    """
    Tests that methods in EmailParams dataclass work expectedly
    """

    def setUp(self) -> None:
        """setup for tests"""
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
            self.assertEqual(val, getattr(res, key))

    def test_from_pack_config_valid(self):
        """
        Tests that from_pack_config() static method works properly
        this method should build a SMTPAccount dataclass from a valid
        stackstorm pack_config and an smtp_account_name
        """
        expected_attrs = {**self.mock_smtp_accounts_config[0]}
        expected_attrs.pop("name")

        res = SMTPAccount.from_pack_config(self.mock_pack_config, "config1")
        for key, val in expected_attrs.items():
            self.assertEqual(val, getattr(res, key))

    @raises(KeyError)
    def test_from_pack_config_invalid_name(self):
        """
        Tests that from_pack_config() method works properly - when given an invalid smtp_account_name
        should raise an error if pack config does not contain entry matching smtp_account_name
        """
        SMTPAccount.from_pack_config(self.mock_pack_config, "invalid-config")

    @raises(ValueError)
    def test_from_pack_config_invalid_pack(self):
        """
        Tests that from_pack_config() method works properly - when given an invalid pack_config
        should raise an error if pack config could not be found
        """
        SMTPAccount.from_pack_config({}, "config1")
