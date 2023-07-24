import unittest
from unittest.mock import patch, NonCallableMock, call
from structs.email_params import EmailParams


class TestEmailParams(unittest.TestCase):
    """
    Tests that methods in EmailParams dataclass work expectedly
    """

    def test_from_dict(self):
        mock_valid_kwargs = {
            "subject": "subject1",
            "email_from": "from@example.com",
            "email_cc": ["cc1@example.com", "cc2@example.com"],
            "attachment_filepaths": ["path/to/file1", "path/to/file2"],
            "body_html": "some html string",
            "body_plaintext": "some string",
        }
        mock_invalid_kwargs = {"to_ignore1": "val1", "to_ignore2": "val2"}

        res = EmailParams.from_dict({**mock_valid_kwargs, **mock_invalid_kwargs})
        for key, val in mock_valid_kwargs.items():
            self.assertEqual(val, getattr(res, key))

    @patch("structs.email_params.EmailParams.from_dict")
    @patch("structs.email_params.TemplateHandler")
    def test_from_template_mappings(self, mock_template_handler, mock_from_dict):
        mock_template_handler.return_value.render_html_template.side_effect = [
            "html rendered template for template-name1\n",
            "html rendered template for template-name2\n",
        ]
        mock_template_handler.return_value.render_plaintext_template.side_effect = [
            "plaintext rendered template for template-name1\n",
            "plaintext rendered template for template-name2\n",
        ]

        mock_from_dict.return_value = NonCallableMock()

        mock_kwargs = {"kwarg1": "val1"}

        mock_template_mappings = {
            "template-name1": {"arg1": "val1", "arg2": "val2"},
            "template-name2": {"arg3": "val3", "arg4": "val4"},
        }

        res = EmailParams.from_template_mappings(
            template_mappings=mock_template_mappings, **mock_kwargs
        )

        mock_template_handler.assert_called_once()
        mock_template_handler.return_value.render_html_template.assert_has_calls(
            [
                call(
                    template_name="template-name1",
                    template_params={"arg1": "val1", "arg2": "val2"},
                ),
                call(
                    template_name="template-name2",
                    template_params={"arg3": "val3", "arg4": "val4"},
                ),
            ]
        )

        mock_template_handler.return_value.render_plaintext_template.assert_has_calls(
            [
                call(
                    template_name="template-name1",
                    template_params={"arg1": "val1", "arg2": "val2"},
                ),
                call(
                    template_name="template-name2",
                    template_params={"arg3": "val3", "arg4": "val4"},
                ),
            ]
        )

        mock_from_dict.assert_called_once_with(
            {
                **mock_kwargs,
                **{
                    "body_html": "html rendered template for template-name1\n"
                    "html rendered template for template-name2\n",
                    "body_plaintext": "plaintext rendered template for template-name1\n"
                    "plaintext rendered template for template-name2\n",
                },
            }
        )
        self.assertEqual(res, mock_from_dict.return_value)
