from email.mime.multipart import MIMEMultipart
from pathlib import Path
from unittest.mock import patch, call, MagicMock, mock_open, NonCallableMock

import pytest

from email_api.emailer import Emailer


@pytest.fixture(name="template_handler", scope="function")
def template_handler_fixture():
    """
    Returns a mock TemplateHandler instance, this will
    generate a new mock for each test, but getting the
    template_handler fixture will return the same mock
    """
    return MagicMock()


@pytest.fixture(name="instance")
def instance_fixture(template_handler):
    """
    Returns a mock Emailer instance, with a mocked
    template injected
    """
    mock_smtp_account = MagicMock()
    return Emailer(mock_smtp_account, template_handler)


@patch("email_api.emailer.Emailer.build_email")
@patch("email_api.emailer.SMTP_SSL")
def test_send_emails(mock_smtp_ssl, mock_build_email, instance):
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

    instance.send_emails(
        emails=[mock_email_param, mock_email_param2],
    )
    mock_smtp_ssl.assert_called_once_with(
        instance.smtp_account.server,
        instance.smtp_account.port,
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


@patch("builtins.open", new_callable=mock_open, read_data="data")
@patch("email_api.emailer.MIMEApplication")
def test_attach_files(mock_mime_application, mock_file, instance):
    """
    Tests that attach_files method works expectedly - with valid filepaths
    method should open file and add as attachment to given MIMEMultipart instance (msg)
    """
    mock_msg = MagicMock()
    mock_filepaths = ["path/to/file1.txt", "path/to/file2.md"]

    mock_mime_application.side_effect = [{}, {}]

    res = instance.attach_files(mock_msg, mock_filepaths)
    assert mock_file.call_args_list == [
        call(
            Path(f"{instance.EMAIL_ATTACHMENTS_ROOT_DIR}/path/to/file1.txt"),
            "rb",
        ),
        call(
            Path(f"{instance.EMAIL_ATTACHMENTS_ROOT_DIR}/path/to/file2.md"),
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
    assert res == mock_msg


@patch("builtins.open", side_effect=FileNotFoundError())
def test_attach_files_invalid_fp(_, instance):
    """
    Tests that attach_files method works expectedly - with invalid filepaths
    should raise a RuntimeError
    """
    mock_msg = NonCallableMock()
    mock_filepaths = ["invalid/path"]

    with pytest.raises(RuntimeError):
        instance.attach_files(mock_msg, mock_filepaths)


@patch("email_api.emailer.Emailer.build_email_body")
def test_build_email_header_fields(mock_build_email_body, instance):
    """
    Tests that build_email works expectedly when given no attachments to add
    Should build email by setting up metadata, then building message body from templates
    """
    mock_email_params = MagicMock()
    mock_email_params.email_to = ["to1@example.com", "to2@example.com"]
    mock_email_params.email_cc = ["cc1@example.com", "cc2@example.com"]
    mock_email_params.attachment_filepaths = None
    mock_email_params.subject = "subject1"

    res = instance.build_email(mock_email_params)

    mock_build_email_body.assert_called_once_with(
        mock_email_params.email_templates, mock_email_params.as_html
    )

    assert isinstance(res, MIMEMultipart)
    assert res.get_payload() == [mock_build_email_body.return_value]
    assert res["To"] == "to1@example.com, to2@example.com"
    assert res["Cc"] == "cc1@example.com, cc2@example.com"
    assert res["From"] == mock_email_params.email_from
    assert res["reply-to"] == mock_email_params.email_from
    assert res["Subject"] == mock_email_params.subject


@patch("email_api.emailer.Emailer.build_email_body")
@patch("email_api.emailer.Emailer.attach_files")
@patch("email_api.emailer.MIMEMultipart")
def test_build_email_with_attachments(
    mock_mime_multipart, mock_attach_files, _, instance
):
    """
    Tests that build_email works expectedly when given no attachments to add
    Should build email by setting up metadata, then building message body from templates
    """
    mock_email_params = MagicMock()
    mock_email_params.attachment_filepaths = NonCallableMock()
    instance.build_email(mock_email_params)
    mock_attach_files.assert_called_once_with(
        mock_mime_multipart.return_value, mock_email_params.attachment_filepaths
    )


@pytest.mark.parametrize("as_html", [True, False])
@patch("email_api.emailer.MIMEText")
def test_build_email_body(mock_mime_text, as_html, instance, template_handler):
    """
    Tests that build email body renders the
    expected templates and places them into the
    expected MIMEText object
    """
    template_details_1 = MagicMock()
    template_details_2 = MagicMock()
    template_list = [template_details_1, template_details_2]

    template_handler.render_html_template.side_effect = [
        "template-render-html-1\n",
        "template-render-html-2\n",
    ]

    template_handler.render_plaintext_template.side_effect = [
        "template-render-plaintext-1\n",
        "template-render-plaintext-2\n",
    ]

    res = instance.build_email_body(template_list, as_html=as_html)
    if as_html:
        assert template_handler.render_html_template.call_count == 2
        assert template_handler.render_plaintext_template.call_count == 0
        assert template_handler.render_html_template.call_args_list == [
            call(template_details_1),
            call(template_details_2),
        ]
        mock_mime_text.assert_called_once_with(
            "template-render-html-1\ntemplate-render-html-2\n", "html"
        )
    else:
        assert template_handler.render_html_template.call_count == 0
        assert template_handler.render_plaintext_template.call_count == 2
        assert template_handler.render_plaintext_template.call_args_list == [
            call(template_details_1),
            call(template_details_2),
        ]
        mock_mime_text.assert_called_once_with(
            "template-render-plaintext-1\ntemplate-render-plaintext-2\n",
            "plain",
            "utf-8",
        )
    assert res == mock_mime_text.return_value
