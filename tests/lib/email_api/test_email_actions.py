import unittest
from unittest.mock import patch, NonCallableMock

from email_api.email_actions import EmailActions

# pylint:disable=protected-access


class TestEmailActions(unittest.TestCase):
    """
    Tests that methods in EmailActions class work expectedly
    """

    def setUp(self) -> None:
        """setup for tests"""
        self.instance = EmailActions()
        self.mock_kwargs = {
            "subject": "subject1",
            "email_from": "from@example.com",
            "email_cc": ["cc1@example.com", "cc2@example.com"],
            "attachment_filepaths": ["path/to/file1", "path/to/file2"],
        }

    @patch("email_api.email_actions.EmailParams")
    def test_setup_email_params(self, mock_email_params):
        mock_templates = {"template1": {"param1": "val1", "param2": "val2"}}

        mock_param_obj = NonCallableMock()
        mock_email_params.from_template_mappings.return_value = mock_param_obj
        res = self.instance._setup_email_params(
            templates=mock_templates, **self.mock_kwargs
        )

        mock_email_params.from_template_mappings.assert_called_once_with(
            template_mappings=mock_templates,
            subject="subject1",
            email_from="from@example.com",
            email_cc=("cc1@example.com", "cc2@example.com"),
            attachment_filepaths=["path/to/file1", "path/to/file2"],
        )

        self.assertEqual(res, mock_param_obj)

    @patch("email_api.email_actions.Emailer")
    @patch("email_api.email_actions.EmailActions._setup_email_params")
    def test_send_test_email(self, mock_setup_email_params, mock_emailer):
        mock_smtp_account = NonCallableMock()
        mock_email_to = ["from@example.com"]
        mock_username = "user1"
        mock_test_message = "This is a test email"

        self.instance.send_test_email(
            smtp_account=mock_smtp_account,
            email_to=mock_email_to,
            username=mock_username,
            test_message=mock_test_message,
            as_html=True,
            **self.mock_kwargs
        )

        mock_setup_email_params.assert_called_once_with(
            templates={
                "test": {"username": mock_username, "test_message": mock_test_message},
                "footer": {},
            },
            **self.mock_kwargs
        )

        mock_emailer.assert_called_once_with(mock_smtp_account)
        mock_emailer.return_value.send_email.assert_called_once_with(
            email_to=(mock_email_to[0],),
            email_params=mock_setup_email_params.return_value,
            as_html=True,
        )
