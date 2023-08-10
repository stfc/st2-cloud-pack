import unittest
from pathlib import Path
from unittest.mock import patch, call, MagicMock, mock_open

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
        with patch("email_api.emailer.TemplateHandler") as mock_template_handler:
            self.template_handler = mock_template_handler
            self.instance = Emailer(mock_template_handler)

    @patch("email_api.emailer.Emailer._build_email")
    @patch("email_api.emailer.SMTP_SSL")
    def test_send_emails(self, mock_smtp_ssl, mock_build_email):
        """
        Tests that send_emails method works expectedly
        Should setup SMTP_SSL connection to web server, and
        iterate through list of EmailParams call sendmail for each
        """
        mock_template_1 = MagicMock()
        mock_template_1.template_name = "mock_template_1"

        mock_template_2 = MagicMock()
        mock_template_2.template_name = "mock_template_2"

        mock_email_param = MagicMock()
        mock_email_param.email_to = ("test1@example.com",)
        mock_email_param.email_from = "from@example.com"
        mock_email_param.email_cc = ("cc1@example.com", "cc2@example.com")
        mock_email_param.email_templates = [mock_template_1, mock_template_2]

        mock_email_param2 = MagicMock()
        mock_email_param2.email_to = ("test2@example.com",)
        mock_email_param2.email_from = "from@example.com"
        mock_email_param2.email_cc = None
        mock_email_param2.email_templates = [mock_template_1]

        mock_server = mock_smtp_ssl.return_value.__enter__.return_value

        self.instance.send_emails(
            emails=[mock_email_param, mock_email_param2],
        )
        mock_smtp_ssl.assert_called_once_with(
            self.instance._smtp_account.server,
            self.instance._smtp_account.port,
            timeout=60,
        )

        mock_server.ehlo.assert_called_once()

        mock_server.sendmail.assert_has_calls(
            [
                call(
                    mock_email_param.email_from,
                    ("test1@example.com", "cc1@example.com", "cc2@example.com"),
                    mock_build_email.return_value.as_string.return_value,
                ),
                call(
                    mock_email_param2.email_from,
                    ("test2@example.com",),
                    mock_build_email.return_value.as_string.return_value,
                ),
            ]
        )

        mock_build_email.assert_has_calls(
            [
                call(mock_email_param),
                call().as_string(),
                call(mock_email_param2),
                call().as_string(),
            ]
        )

    # pylint:disable=too-many-arguments

    @parameterized.expand(
        [
            ("with ccs & attachments", ("cc1@example.com"), ["fp1", "fp2"]),
            ("no ccs & attachments", None, ["fp1", "fp2"]),
            ("with ccs & no attachments", ("cc1@example.com", "cc2@example.com"), None),
            ("no ccs & no attachments", None, None),
        ]
    )
    @patch("email_api.emailer.Emailer._build_email_body")
    @patch("email_api.emailer.Emailer._attach_files")
    @patch("email_api.emailer.MIMEMultipart")
    def test_build_email(
        self,
        _,
        mock_ccs,
        mock_attachment_filepaths,
        mock_mime_multipart,
        mock_attach_files,
        mock_build_email_body,
    ):
        """
        Tests that build_email works expectedly when given no attachments to add
        Should build email by setting up metadata, then building message body from templates
        """
        mock_email_params = MagicMock()
        mock_email_params.email_cc.return_value = mock_ccs
        mock_email_params.attachment_filepaths = mock_attachment_filepaths

        res = self.instance._build_email(mock_email_params)

        mock_mime_multipart.assert_called_once()

        mock_build_email_body.assert_called_once_with(
            mock_email_params.email_templates, mock_email_params.as_html
        )

        if mock_attachment_filepaths:
            mock_attach_files.assert_called_once_with(
                mock_mime_multipart.return_value, mock_email_params.attachment_filepaths
            )
            self.assertEqual(res, mock_attach_files.return_value)
        else:
            self.assertEqual(res, mock_mime_multipart.return_value)

    @parameterized.expand(
        [("test_with_as_html_true", True), ("test_with_as_html_false", False)]
    )
    @patch("email_api.emailer.MIMEText")
    def test_build_email_body(self, _, as_html, mock_mime_text):
        template_details_1 = MagicMock()
        template_details_2 = MagicMock()
        template_list = [template_details_1, template_details_2]

        self.instance._template_handler.render_html_template.side_effect = [
            "template-render-html-1\n",
            "template-render-html-2\n",
        ]

        self.instance._template_handler.render_plaintext_template.side_effect = [
            "template-render-plaintext-1\n",
            "template-render-plaintext-2\n",
        ]

        res = self.instance._build_email_body(template_list, as_html=as_html)
        if as_html:
            self.assertEqual(
                self.instance._template_handler.render_html_template.call_args_list,
                [call(template_details_1), call(template_details_2)],
            )
            mock_mime_text.assert_called_once_with(
                "template-render-html-1\ntemplate-render-html-2\n", "html"
            )
        else:
            self.assertEqual(
                self.instance._template_handler.render_plaintext_template.call_args_list,
                [call(template_details_1), call(template_details_2)],
            )
            mock_mime_text.assert_called_once_with(
                "template-render-plaintext-1\ntemplate-render-plaintext-2\n",
                "plain",
                "utf-8",
            )
        self.assertEqual(res, mock_mime_text.return_value)

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch("email_api.emailer.MIMEApplication")
    def test_attach_files(self, mock_mime_application, mock_file):
        """
        Tests that attach_files method works expectedly - with valid filepaths
        method should open file and add as attachment to given MIMEMultipart instance (msg)
        """
        mock_msg = MagicMock()
        mock_filepaths = ["path/to/file1.txt", "path/to/file2.md"]

        mock_mime_application.side_effect = [{}, {}]

        res = self.instance._attach_files(mock_msg, mock_filepaths)
        assert mock_file.call_args_list == [
            call(
                Path(f"{self.instance.EMAIL_ATTACHMENTS_ROOT_DIR}/path/to/file1.txt"),
                "rb",
            ),
            call(
                Path(f"{self.instance.EMAIL_ATTACHMENTS_ROOT_DIR}/path/to/file2.md"),
                "rb",
            ),
        ]

        mock_mime_application.assert_has_calls(
            [call("data", Name="file1.txt"), call("data", Name="file2.md")]
        )

        mock_msg.attach.assert_has_calls(
            [
                call({"Content-Disposition": "attachment; filename=file1.txt"}),
                call({"Content-Disposition": "attachment; filename=file2.md"}),
            ]
        )
        self.assertEqual(res, mock_msg)

    @raises(RuntimeError)
    @patch("builtins.open", side_effect=FileNotFoundError())
    def test_attach_files_invalid_fp(self, _):
        """
        Tests that attach_files method works expectedly - with invalid filepaths
        should raise a RuntimeError
        """
        mock_msg = MagicMock()
        mock_filepaths = ["invalid/path"]
        self.instance._attach_files(mock_msg, mock_filepaths)