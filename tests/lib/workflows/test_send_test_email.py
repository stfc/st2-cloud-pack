from unittest.mock import patch, NonCallableMock
import pytest

from structs.email.email_template_details import EmailTemplateDetails
from workflows.send_test_email import send_test_email


@pytest.fixture(name="send_test_email_test_case")
def send_test_email_test_case_fixture():
    """
    Fixture to run send_test_email test cases
    """

    @patch("workflows.send_test_email.Emailer")
    @patch("workflows.send_test_email.EmailParams")
    def _send_test_email_test_case(
        mock_kwargs, expected_kwargs, cc_cloud_support, mock_email_params, mock_emailer
    ):
        """
        runs a test case for send_test_email function
        :param mock_kwargs: The kwargs to pass to send_test_email
        :param expected_kwargs: what kwargs we expect to pass to EmailParams dataclass
        :param
        """
        mock_smtp_account = NonCallableMock()
        mock_username = "user1"
        mock_test_message = "This is a test email"

        send_test_email(
            smtp_account=mock_smtp_account,
            username=mock_username,
            test_message=mock_test_message,
            cc_cloud_support=cc_cloud_support,
            **mock_kwargs
        )
        mock_email_params.from_dict.assert_called_once_with(
            {
                **{
                    "email_templates": [
                        EmailTemplateDetails(
                            template_name="test",
                            template_params={
                                "username": mock_username,
                                "test_message": mock_test_message,
                            },
                        ),
                        EmailTemplateDetails(
                            template_name="footer",
                        ),
                    ]
                },
                **expected_kwargs,
            }
        )

        mock_emailer.assert_called_once_with(mock_smtp_account)
        mock_emailer.return_value.send_emails.assert_called_once_with(
            [mock_email_params.from_dict.return_value]
        )

    return _send_test_email_test_case


def test_send_test_email_with_cc(send_test_email_test_case):
    """
    Tests that send_test_email method works expectedly
    Should create an appropriate EmailParams using test and footer templates, then send an email via an
    Emailer object. Must include cloud-support@stfc.ac.uk in email_cc list
    """
    mock_kwargs = {
        "email_to": ("test@example.com",),
        "subject": "subject1",
        "email_from": "from@example.com",
        "email_cc": ["cc1@example.com", "cc2@example.com"],
        "attachment_filepaths": ["path/to/file1", "path/to/file2"],
        "as_html": True,
    }

    expected_kwargs = mock_kwargs
    # since cc_cloud_support=True, expected email_cc should include it
    expected_kwargs["email_cc"].append("cloud-support@stfc.ac.uk")

    send_test_email_test_case(mock_kwargs, expected_kwargs, True)


def test_send_test_email_no_cc(send_test_email_test_case):
    """
    Tests that send_test_email method works expectedly
    Should create an appropriate EmailParams using test and footer templates, then send an email via an
    Emailer object. Must not include cloud-support@stfc.ac.uk in email_cc list
    """
    mock_kwargs = {
        "email_to": ("test@example.com",),
        "subject": "subject1",
        "email_from": "from@example.com",
        "email_cc": ["cc1@example.com", "cc2@example.com"],
        "attachment_filepaths": ["path/to/file1", "path/to/file2"],
        "as_html": True,
    }
    expected_kwargs = mock_kwargs
    send_test_email_test_case(mock_kwargs, expected_kwargs, False)
