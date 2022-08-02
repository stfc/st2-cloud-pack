import unittest
from unittest import mock

from email_api.email_api import EmailApi
from nose.tools import raises


class EmailApiTests(unittest.TestCase):
    TEST_ACCOUNTS = [
        {"name": "default", "username": "test", "password": "password"},
        {"name": "test"},
    ]

    def setUp(self) -> None:
        self.api = EmailApi()

    @raises(FileNotFoundError)
    def test_load_template_file_not_found(self):
        """
        Tests that load_template can raise a FileNotFoundError
        """
        self.assertRaises(FileNotFoundError, self.api.load_template("test"))

    @raises(ValueError, KeyError)
    def test_load_smtp_account_errors(self):
        """
        Tests that load_smtp_account raises the appropriate errors
        """
        self.assertRaises(ValueError, self.api.load_smtp_account({}, "default"))
        self.assertRaises(
            KeyError,
            self.api.load_smtp_account(
                {{"name": "default"}, {"name": "test"}}, "invalid"
            ),
        )

    def test_load_smtp_account(self):
        """
        Tests that load_smtp_account works correctly
        """
        account = {"name": "default", "username": "test", "password": "password"}
        result = self.api.load_smtp_account(EmailApiTests.TEST_ACCOUNTS, "default")
        self.assertEqual(result, account)

    # Expect error as would need to mock both open and os.path.exists for this to function
    @raises(FileNotFoundError)
    def test_send_emails(self):
        """
        Tests that send_emails will send multiple emails
        """
        result = self.api.send_emails(
            smtp_accounts=EmailApiTests.TEST_ACCOUNTS,
            emails={"email1": "Message 1", "email2": "Message 2"},
            subject="Subject",
            email_from="test@example.com",
            email_cc="test-cc@example.com",
            header="",
            footer="",
            attachment_filepaths=[],
            smtp_account="default",
            test_override=False,
            test_override_email="OverrideEmail",
            send_as_html=True,
        )
        self.api.send_email.assert_has_calls(
            [
                mock.call(
                    smtp_accounts=EmailApiTests.TEST_ACCOUNTS,
                    subject="Subject",
                    email_to="email1",
                    email_from="test@example.com",
                    email_cc="test-cc@example.com",
                    header="",
                    footer="",
                    body="Message",
                    attachment_filepaths=[],
                    smtp_account="default",
                    send_as_html=True,
                ),
                mock.call(
                    smtp_accounts=EmailApiTests.TEST_ACCOUNTS,
                    subject="Subject",
                    email_to="email2",
                    email_from="test@example.com",
                    email_cc="test-cc@example.com",
                    header="",
                    footer="",
                    body="Message",
                    attachment_filepaths=[],
                    smtp_account="default",
                    send_as_html=True,
                ),
            ]
        )
        self.assertEqual(result, True)

    # Expect error as would need to mock both open and os.path.exists for this to function
    @raises(FileNotFoundError)
    def test_send_emails_override(self):
        """
        Tests that send_emails will send multiple emails to the test override when enabled
        """
        result = self.api.send_emails(
            smtp_accounts=EmailApiTests.TEST_ACCOUNTS,
            emails={"email1": "Message 1", "email2": "Message 2"},
            subject="Subject",
            email_from="test@example.com",
            email_cc="test-cc@example.com",
            header="",
            footer="",
            attachment_filepaths=[],
            smtp_account="default",
            test_override=True,
            test_override_email="OverrideEmail",
            send_as_html=True,
        )
        self.api.send_email.assert_has_calls(
            [
                mock.call(
                    smtp_accounts=EmailApiTests.TEST_ACCOUNTS,
                    subject="Subject",
                    email_to="OverrideEmail",
                    email_from="test@example.com",
                    email_cc="test-cc@example.com",
                    header="",
                    footer="",
                    body="Message",
                    attachment_filepaths=[],
                    smtp_account="default",
                    send_as_html=True,
                ),
                mock.call(
                    smtp_accounts=EmailApiTests.TEST_ACCOUNTS,
                    subject="Subject",
                    email_to="OverrideEmail",
                    email_from="test@example.com",
                    email_cc="test-cc@example.com",
                    header="",
                    footer="",
                    body="Message",
                    attachment_filepaths=[],
                    smtp_account="default",
                    send_as_html=True,
                ),
            ]
        )
        self.assertEqual(result, True)
