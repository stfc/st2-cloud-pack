import unittest
from nose.tools import raises

from email_api.email_helpers import EmailHelpers


class EmailHelperTests(unittest.TestCase):
    TEST_ACCOUNTS = [
        {
            "name": "default",
            "username": "test",
            "password": "password",
            "server": "test.server",
            "port": 123,
            "secure": False,
            "smtp_auth": False,
        },
        {
            "name": "test",
            "username": "test",
            "password": "password",
            "server": "test.server",
            "port": 123,
            "secure": True,
            "smtp_auth": True,
        },
    ]

    TEST_CONFIG = {"smtp_accounts": TEST_ACCOUNTS}

    def setUp(self) -> None:
        pass

    @raises(ValueError)
    def test_load_smtp_account_value_error(self):
        """
        Tests that load_smtp_account raises a value error when no accounts are supplied
        """
        EmailHelpers.load_smtp_account({}, "default")

    @raises(KeyError)
    def test_load_smtp_account_key_error(self):
        """
        Tests that load_smtp_account raises a key error when the smtp_account doesn't exist
        """
        EmailHelpers.load_smtp_account(EmailHelperTests.TEST_CONFIG, "invalid")

    def test_load_smtp_account(self):
        """
        Tests that load_smtp_account works correctly
        """
        result = EmailHelpers.load_smtp_account(EmailHelperTests.TEST_CONFIG, "default")
        expected_result = EmailHelperTests.TEST_ACCOUNTS[0]
        del expected_result["name"]
        self.assertEqual(expected_result, result.__dict__)
