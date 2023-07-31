import unittest
from unittest.mock import patch, NonCallableMock

from email_api.email_actions import EmailActions
from structs.email.email_template_details import EmailTemplateDetails

# pylint:disable=protected-access


class TestEmailActions(unittest.TestCase):
    """
    Tests that methods in EmailActions class work expectedly
    """

    def setUp(self) -> None:
        """setup for tests"""
        self.instance = EmailActions()
        self.mock_kwargs = {
            "email_to": ("test@example.com",),
            "subject": "subject1",
            "email_from": "from@example.com",
            "email_cc": ["cc1@example.com", "cc2@example.com"],
            "attachment_filepaths": ["path/to/file1", "path/to/file2"],
            "as_html": True,
        }

    @patch("email_api.email_actions.EmailParams")
    def test_setup_email_params(self, mock_email_params):
        """
        Tests that _setup_email_params works expectedly
        Should return an EmailParams dataclass which has attributes matching parameter values given
        """
        mock_email_template1 = NonCallableMock()
        mock_email_template2 = NonCallableMock()

        mock_param_obj = NonCallableMock()
        mock_email_params.from_dict.return_value = mock_param_obj
        res = self.instance._setup_email_params(
            email_templates=[mock_email_template1, mock_email_template2],
            **self.mock_kwargs
        )

        exp = {"email_templates": [mock_email_template1, mock_email_template2]}

        mock_email_params.from_dict.assert_called_once_with({**exp, **self.mock_kwargs})
        self.assertEqual(res, mock_param_obj)

    @patch("email_api.email_actions.Emailer")
    @patch("email_api.email_actions.EmailActions._setup_email_params")
    def test_send_test_email(self, mock_setup_email_params, mock_emailer):
        """
        Tests that send_test_email method works expectedly
        Should create an appropriate EmailParams using test and footer templates, then send an email via an
        Emailer object
        """
        mock_smtp_account = NonCallableMock()
        mock_username = "user1"
        mock_test_message = "This is a test email"

        self.instance.send_test_email(
            smtp_account=mock_smtp_account,
            username=mock_username,
            test_message=mock_test_message,
            **self.mock_kwargs
        )

        mock_setup_email_params.assert_called_once_with(
            email_templates=[
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
            ],
            **self.mock_kwargs
        )

        mock_emailer.assert_called_once_with(mock_smtp_account)
        mock_emailer.return_value.send_emails.assert_called_once_with(
            [mock_setup_email_params.return_value]
        )
