import unittest
from unittest import mock
from unittest.mock import ANY, MagicMock, patch

from email_api.email_api import EmailApi
from nose.tools import raises


# Avoid actually attempting to send any emails
from structs.email_params import EmailParams
from structs.smtp_account import SMTPAccount


@patch("email_api.email_api.SMTP_SSL")
class EmailApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.api = EmailApi()
        self.test_account = SMTPAccount(
            username="test",
            password="password",
            server="test.server",
            port=123,
            secure=False,
            smtp_auth=False,
        )

    @raises(FileNotFoundError)
    def test_load_template_file_not_found(self, _):
        """
        Tests that load_template can raise a FileNotFoundError
        """
        self.api.load_template("test")

    def test_send_email_insecure(self, smtp_mock):
        """
        Tests that send_email functions as expected
        """
        # Replace to avoid attempting to load files
        self.api.load_template = MagicMock(return_value="")

        email_params = EmailParams(
            subject="Subject",
            email_from="test@example.com",
            email_cc=["test-cc@example.com"],
            header="",
            footer="",
            attachment_filepaths=[],
            send_as_html=True,
            test_override=False,
            test_override_email=[""],
        )

        result = self.api.send_email(
            smtp_account=self.test_account,
            email_params=email_params,
            email_to=["test@example.com"],
            body="Message",
        )

        self.assertEqual(result, (True, "Email sent"))

        smtp_mock.assert_called_once_with(
            self.test_account.server, self.test_account.port, timeout=60
        )
        smtp_mock_instance = smtp_mock.return_value
        smtp_mock_instance.ehlo.assert_called_once()
        smtp_mock_instance.starttls.assert_not_called()
        smtp_mock_instance.login.assert_not_called()

        smtp_mock_instance.sendmail.assert_called_once_with(
            "test@example.com",
            ["test@example.com", "test-cc@example.com"],
            ANY,
        )

    def test_send_email_secure(self, smtp_mock):
        """
        Tests that send_email functions as expected
        """
        # Replace to avoid attempting to load files
        self.api.load_template = MagicMock(return_value="")

        self.test_account.secure = True
        self.test_account.smtp_auth = True

        email_params = EmailParams(
            subject="Subject",
            email_from="test@example.com",
            email_cc=["test-cc@example.com"],
            header="",
            footer="",
            attachment_filepaths=[],
            send_as_html=True,
            test_override=False,
            test_override_email=[""],
        )

        result = self.api.send_email(
            smtp_account=self.test_account,
            email_params=email_params,
            email_to=["test@example.com"],
            body="Message",
        )

        self.assertEqual(result, (True, "Email sent"))

        smtp_mock.assert_called_once_with(
            self.test_account.server, self.test_account.port, timeout=60
        )
        smtp_mock_instance = smtp_mock.return_value
        smtp_mock_instance.ehlo.assert_called_once()
        smtp_mock_instance.starttls.assert_called_once()
        smtp_mock_instance.login.assert_called_once_with("test", "password")

        smtp_mock_instance.sendmail.assert_called_once_with(
            "test@example.com",
            ["test@example.com", "test-cc@example.com"],
            ANY,
        )

    def test_send_email_override(self, smtp_mock):
        """
        Tests that send_email functions as expected
        """
        # Replace to avoid attempting to load files
        self.api.load_template = MagicMock(return_value="")

        self.test_account.secure = True
        self.test_account.smtp_auth = True

        email_params = EmailParams(
            subject="Subject",
            email_from="test@example.com",
            email_cc=["test-cc@example.com"],
            header="",
            footer="",
            attachment_filepaths=[],
            send_as_html=True,
            test_override=True,
            test_override_email=["override@example.com"],
        )

        result = self.api.send_email(
            smtp_account=self.test_account,
            email_params=email_params,
            email_to=["test@example.com"],
            body="Message",
        )

        self.assertEqual(result, (True, "Email sent"))

        smtp_mock.assert_called_once_with(
            self.test_account.server, self.test_account.port, timeout=60
        )
        smtp_mock_instance = smtp_mock.return_value
        smtp_mock_instance.ehlo.assert_called_once()
        smtp_mock_instance.starttls.assert_called_once()
        smtp_mock_instance.login.assert_called_once_with("test", "password")

        smtp_mock_instance.sendmail.assert_called_once_with(
            "test@example.com",
            ["override@example.com"],
            ANY,
        )

    def test_send_emails(self, _):
        """
        Tests that send_emails will send multiple emails
        """
        # Replace to avoid attempting to load files/actually send an email in testing
        self.api.load_template = MagicMock(return_value="")
        self.api.send_email = MagicMock(return_value=(True, "Email sent"))

        email_params = EmailParams(
            subject="Subject",
            email_from="test@example.com",
            email_cc=["test-cc@example.com"],
            header="",
            footer="",
            attachment_filepaths=[],
            test_override=False,
            test_override_email=["OverrideEmail"],
            send_as_html=True,
        )

        result = self.api.send_emails(
            smtp_account=self.test_account,
            emails={"email1": "Message 1", "email2": "Message 2"},
            email_params=email_params,
        )
        self.api.send_email.assert_has_calls(
            [
                mock.call(
                    smtp_account=self.test_account,
                    email_params=email_params,
                    email_to=["email1"],
                    body="Message 1",
                ),
                mock.call(
                    smtp_account=self.test_account,
                    email_params=email_params,
                    email_to=["email2"],
                    body="Message 2",
                ),
            ],
            any_order=True,
        )
        self.assertEqual(result, True)

    # Expect error as would need to mock both open and os.path.exists for this to function
    @raises(FileNotFoundError)
    def test_send_emails_override(self, _):
        """
        Tests that send_emails will send multiple emails to the test override when enabled
        """
        email_params = EmailParams(
            subject="Subject",
            email_from="test@example.com",
            email_cc=["test-cc@example.com"],
            header="",
            footer="",
            attachment_filepaths=[],
            test_override=True,
            test_override_email=["OverrideEmail"],
            send_as_html=True,
        )
        result = self.api.send_emails(
            smtp_account=self.test_account,
            emails={"email1": "Message 1", "email2": "Message 2"},
            email_params=email_params,
        )
        self.api.send_email.assert_has_calls(
            [
                mock.call(
                    smtp_account=self.test_account,
                    email_params=email_params,
                    email_to="OverrideEmail",
                    body="Message",
                ),
                mock.call(
                    smtp_account=self.test_account,
                    email_params=email_params,
                    email_to="OverrideEmail",
                    body="Message",
                ),
            ]
        )
        self.assertEqual(result, True)
