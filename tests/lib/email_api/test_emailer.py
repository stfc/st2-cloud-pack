import os
import unittest
from unittest.mock import patch, call, NonCallableMock, MagicMock, mock_open

from nose.tools import raises
from parameterized import parameterized

from email_api.emailer import Emailer

# pylint:disable=protected-access


class TestEmailer(unittest.TestCase):
    """
    Tests that methods in Emailer class work expectedly
    """

    def setUp(self) -> None:
        """setup for tests"""
        self.mock_smtp_account = MagicMock()
        self.instance = Emailer(self.mock_smtp_account)

    @patch("email_api.emailer.Emailer.send_email")
    def test_send_emails(self, mock_send_email):
        mock_email_param = MagicMock()
        mock_email_param2 = MagicMock()
        mock_emails_dict = {
            ("email-address1", "email-address2"): mock_email_param,
            ("email-address3", "email-address4"): mock_email_param2,
        }
        as_html_flag = True
        self.instance.send_emails(mock_emails_dict, as_html_flag)
        mock_send_email.assert_has_calls(
            [
                call(
                    ("email-address1", "email-address2"), mock_email_param, as_html_flag
                ),
                call(
                    ("email-address3", "email-address4"),
                    mock_email_param2,
                    as_html_flag,
                ),
            ]
        )

    @patch("email_api.emailer.Emailer._build_message")
    @patch("email_api.emailer.Emailer._setup_smtp")
    @patch("email_api.emailer.SMTP_SSL")
    def test_send_email(self, mock_smtp_ssl, mock_setup_smtp, mock_build_message):

        mock_email_param = MagicMock()
        mock_email_to = ("example@example.com",)

        mock_email_msg = MagicMock()
        mock_build_message.return_value = mock_email_msg

        mock_server = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server

        mock_setup_server = MagicMock()
        mock_setup_smtp.return_value = mock_setup_server

        self.instance.send_email(mock_email_to, mock_email_param)

        mock_smtp_ssl.asset_called_once_with(
            self.mock_smtp_account.server, self.mock_smtp_account.port, timeout=60
        )

        mock_setup_smtp.assert_called_once_with(mock_server, self.mock_smtp_account)

        mock_setup_server.sendmail.assert_called_once_with(
            mock_email_param.email_from,
            mock_email_to,
            mock_email_msg.as_string.return_value,
        )

    @parameterized.expand(
        [
            ("secure flag True, smtp_auth False", True, False),
            ("secure flag False, smtp_auth flag True", False, True),
            ("both False", False, False),
            ("both True", True, True),
        ]
    )
    def test_setup_smtp(self, _, secure_flag, smtp_auth_flag):
        mock_server = MagicMock()
        mock_smtp_account = MagicMock()

        mock_smtp_account.secure = secure_flag
        mock_smtp_account.smtp_auth = smtp_auth_flag

        res = self.instance._setup_smtp(mock_server, mock_smtp_account)
        mock_server.ehlo.assert_called_once()
        if secure_flag:
            mock_server.starttls.assert_called_once()
        if smtp_auth_flag:
            mock_server.login.assert_called_once_with(
                mock_smtp_account.username, mock_smtp_account.password
            )
        self.assertEqual(mock_server, res)

    @parameterized.expand(
        [("build plaintext message", True), ("build html message", True)]
    )
    @patch("email_api.emailer.Emailer._setup_email_metadata")
    @patch("email_api.emailer.MIMEText")
    def test_build_message_no_attachments(
        self, _, as_html_flag, mock_mime_text, mock_setup_email_metadata
    ):
        mock_email_params = MagicMock()
        mock_email_params.attachment_filepaths.return_value = None

        mock_email_to = ("example@example.com",)

        mock_msg = MagicMock()
        mock_setup_email_metadata.return_value = mock_msg

        res = self.instance._build_message(
            mock_email_params, mock_email_to, as_html=as_html_flag
        )

        mock_setup_email_metadata.assert_called_once_with(
            mock_email_to, mock_email_params.email_from, mock_email_params.subject
        )

        if as_html_flag:
            mock_mime_text.assert_called_once_with(mock_email_params.body_html, "html")
        else:
            mock_mime_text.assert_called_once_with(
                mock_email_params.body_plaintext, "plain", "utf-8"
            )

        self.assertEqual(res, mock_msg)

    @patch("email_api.emailer.Emailer._setup_email_metadata")
    @patch("email_api.emailer.MIMEText")
    @patch("email_api.emailer.Emailer._attach_files")
    def test_build_message_with_attachments(
        self,
        mock_attach_files,
        mock_mime_text,
        mock_setup_email_metadata,
    ):
        mock_email_params = MagicMock()
        mock_email_params.attachment_filepaths.return_value = ["fp1", "fp2"]
        mock_email_to = ("example@example.com",)

        mock_msg = MagicMock()
        mock_setup_email_metadata.return_value = mock_msg

        mock_res = NonCallableMock()
        mock_attach_files.return_value = mock_res

        res = self.instance._build_message(
            mock_email_params, mock_email_to, as_html=True
        )

        mock_setup_email_metadata.assert_called_once_with(
            mock_email_to, mock_email_params.email_from, mock_email_params.subject
        )

        mock_mime_text.assert_called_once_with(mock_email_params.body_html, "html")

        mock_attach_files.assert_called_once_with(
            mock_msg, mock_email_params.attachment_filepaths
        )
        self.assertEqual(res, mock_res)

    @patch("email_api.emailer.Header")
    @patch("email_api.emailer.formatdate")
    @patch("email_api.emailer.MIMEMultipart")
    def test_setup_metadata(self, mock_mime_multipart, mock_formatdate, mock_header):
        mock_mime_multipart.return_value = {}
        res = self.instance._setup_email_metadata(
            email_to=("example@example.com",),
            email_from="from@example.com",
            subject="test email subject",
            email_cc=["extra@example.com", "extra2@example.com"],
        )
        mock_mime_multipart.assert_called_once()
        mock_header.assert_called_once_with("test email subject", "utf-8")
        mock_formatdate.assert_called_once_with(localtime=True)
        self.assertEqual(
            res,
            {
                "Subject": mock_header.return_value,
                "From": "from@example.com",
                "To": "example@example.com",
                "Date": mock_formatdate.return_value,
                "Cc": "extra@example.com, extra2@example.com",
            },
        )

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch("email_api.emailer.MIMEApplication")
    def test_attach_files(self, mock_mime_application, mock_file):
        mock_msg = MagicMock()
        mock_filepaths = ["path/to/file1", "path/to/file2"]

        mock_mime_application.side_effect = [{}, {}]

        res = self.instance._attach_files(mock_msg, mock_filepaths)
        assert mock_file.call_args_list == [
            call(
                os.path.normpath(
                    os.path.join(
                        self.instance.EMAIL_ATTACHMENTS_ROOT_DIR, "path/to/file1"
                    )
                ),
                "rb",
            ),
            call(
                os.path.normpath(
                    os.path.join(
                        self.instance.EMAIL_ATTACHMENTS_ROOT_DIR, "path/to/file2"
                    )
                ),
                "rb",
            ),
        ]

        mock_mime_application.assert_has_calls(
            [call("data", Name="file1"), call("data", Name="file2")]
        )

        mock_msg.attach.assert_has_calls(
            [
                call({"Content-Disposition": "attachment; filename=file1"}),
                call({"Content-Disposition": "attachment; filename=file2"}),
            ]
        )
        self.assertEqual(res, mock_msg)

    @raises(RuntimeError)
    @patch("builtins.open", side_effect=FileNotFoundError())
    def test_attach_files_invalid_fp(self, _):
        mock_msg = MagicMock()
        mock_filepaths = ["invalid/path"]
        self.instance._attach_files(mock_msg, mock_filepaths)
