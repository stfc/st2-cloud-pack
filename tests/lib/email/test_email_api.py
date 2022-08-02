import smtplib
import unittest
from unittest import mock
from unittest.mock import ANY, MagicMock, create_autospec

from email_api.email_api import EmailApi
from nose.tools import raises


class EmailApiTests(unittest.TestCase):
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
        result = self.api.load_smtp_account(EmailApiTests.TEST_ACCOUNTS, "default")
        self.assertEqual(result, EmailApiTests.TEST_ACCOUNTS[0])

    def test_send_email_insecure(self):
        """
        Tests that send_email functions as expected
        """
        # Replace to avoid attempting to load files
        self.api.load_template = MagicMock(return_value="")

        # Avoid actually attempting to send any emails
        with mock.patch("email_api.email_api.SMTP_SSL") as smtp_mock:
            result = self.api.send_email(
                smtp_accounts=EmailApiTests.TEST_ACCOUNTS,
                subject="Subject",
                email_to=["test@example.com"],
                email_from="test@example.com",
                email_cc=["test-cc@example.com"],
                header="",
                footer="",
                body="Message",
                attachment_filepaths=[],
                smtp_account="default",
                send_as_html=True,
            )

            self.assertEqual(result, (True, "Email sent"))

            smtp_mock.assert_called_once_with("test.server", "123", timeout=60)
            smtp_mock_instance = smtp_mock.return_value
            smtp_mock_instance.ehlo.assert_called_once()
            smtp_mock_instance.starttls.assert_not_called()
            smtp_mock_instance.login.assert_not_called()

            smtp_mock_instance.sendmail.assert_called_once_with(
                "test@example.com",
                ["test@example.com", "test-cc@example.com"],
                ANY,
            )

    def test_send_email_secure(self):
        """
        Tests that send_email functions as expected
        """
        # Replace to avoid attempting to load files
        self.api.load_template = MagicMock(return_value="")

        # Avoid actually attempting to send any emails
        with mock.patch("email_api.email_api.SMTP_SSL") as smtp_mock:
            result = self.api.send_email(
                smtp_accounts=EmailApiTests.TEST_ACCOUNTS,
                subject="Subject",
                email_to=["test@example.com"],
                email_from="test@example.com",
                email_cc=["test-cc@example.com"],
                header="",
                footer="",
                body="Message",
                attachment_filepaths=[],
                smtp_account="test",
                send_as_html=True,
            )

            self.assertEqual(result, (True, "Email sent"))

            smtp_mock.assert_called_once_with("test.server", "123", timeout=60)
            smtp_mock_instance = smtp_mock.return_value
            smtp_mock_instance.ehlo.assert_called_once()
            smtp_mock_instance.starttls.assert_called_once()
            smtp_mock_instance.login.assert_called_once_with("test", "password")

            smtp_mock_instance.sendmail.assert_called_once_with(
                "test@example.com",
                ["test@example.com", "test-cc@example.com"],
                ANY,
            )

    def test_send_emails(self):
        """
        Tests that send_emails will send multiple emails
        """
        # Replace to avoid attempting to load files/actually send an email in testing
        self.api.load_template = MagicMock(return_value="")
        self.api.send_email = MagicMock(return_value=(True, "Email sent"))

        result = self.api.send_emails(
            smtp_accounts=EmailApiTests.TEST_ACCOUNTS,
            emails={"email1": "Message 1", "email2": "Message 2"},
            subject="Subject",
            email_from="test@example.com",
            email_cc=["test-cc@example.com"],
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
                    email_to=["email1"],
                    email_from="test@example.com",
                    email_cc=["test-cc@example.com"],
                    header="",
                    footer="",
                    body="Message 1",
                    attachment_filepaths=[],
                    smtp_account="default",
                    send_as_html=True,
                ),
                mock.call(
                    smtp_accounts=EmailApiTests.TEST_ACCOUNTS,
                    subject="Subject",
                    email_to=["email2"],
                    email_from="test@example.com",
                    email_cc=["test-cc@example.com"],
                    header="",
                    footer="",
                    body="Message 2",
                    attachment_filepaths=[],
                    smtp_account="default",
                    send_as_html=True,
                ),
            ],
            any_order=True,
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
            email_cc=["test-cc@example.com"],
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
                    email_cc=["test-cc@example.com"],
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
                    email_cc=["test-cc@example.com"],
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
