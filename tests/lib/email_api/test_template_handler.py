import unittest
from unittest.mock import patch, mock_open, NonCallableMock, MagicMock
from parameterized import parameterized

from yaml import YAMLError
from nose.tools import raises

from jinja2.exceptions import TemplateError, TemplateNotFound
from exceptions.email_template_error import EmailTemplateError
from email_api.template_handler import TemplateHandler

# pylint:disable=protected-access


class TestTemplateHandler(unittest.TestCase):
    """
    Tests that methods in TemplateHandler class works expectedly
    """

    def setUp(self) -> None:
        """setup for tests"""
        self.mock_template_metadata = {
            "mock-template": {
                "html_filepath": "/path/to/file.html",
                "plaintext_filepath": "/path/to/file.txt",
                "schema": {"attr1": None, "attr2": "abc", "attr3": "def"},
            },
            "mock-template-no-schema": {
                "html_filepath": "/path/to/file2.html",
                "plaintext_filepath": "/path/to/file2.txt",
                "schema": None,
            },
            "mock-template-misconfigured": {"schema": None},
        }
        self.mock_template_env = MagicMock()

        with patch(
            "email_api.template_handler.TemplateHandler._load_all_metadata",
            return_value=self.mock_template_metadata,
        ):
            self.instance = TemplateHandler()
            self.instance._template_env = self.mock_template_env

    @patch("email_api.template_handler.safe_load")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_all_metadata_valid(self, mock_file, mock_yaml_load):
        """
        Test that load_all_metadata method functions expectedly
        Reads yaml file containing metadata info set in EMAIL_TEMPLATE_METADATA_FP
        """
        safe_load_out = NonCallableMock()
        mock_yaml_load.return_value = safe_load_out

        res = self.instance._load_all_metadata()
        mock_file.assert_called_once_with(
            self.instance.EMAIL_TEMPLATE_METADATA_FP, "r", encoding="utf-8"
        )
        mock_yaml_load.assert_called_once_with(mock_file.return_value)
        self.assertEqual(res, safe_load_out)

    @raises(EmailTemplateError)
    @patch("email_api.template_handler.safe_load")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_all_metadata_invalid(self, _, mock_yaml_load):
        """
        Tests that load_all_metadata method functions expectedly
        Raises error if yaml file cannot be read
        """

        mock_yaml_load.side_effect = YAMLError()
        self.instance._load_all_metadata()

    @parameterized.expand(
        [
            (
                "with emtpy given vals, use defaults",
                {"attr1": "def1", "attr2": "def2", "attr3": "def3"},
                {},
                {"attr1": "def1", "attr2": "def2", "attr3": "def3"},
            ),
            (
                "with given vals and defaults, use given vals",
                {"attr1": "def1", "attr2": "def2", "attr3": "def3"},
                {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
                {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
            ),
            (
                "with given vals and no defaults, use given vals",
                {"attr1": None, "attr2": None, "attr3": None},
                {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
                {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
            ),
            (
                "with given vals set as None, use defaults",
                {"attr1": None, "attr2": None, "attr3": None},
                {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
                {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
            ),
            (
                "mix of given vals and defaults, use given vals if available else defaults",
                {"attr1": None, "attr2": "def2", "attr3": "def3"},
                {"attr1": "val1", "attr2": None},
                {"attr1": "val1", "attr2": "def2", "attr3": "def3"},
            ),
        ]
    )
    def test_parse_template_attrs_valid(
        self, _, mock_schema, mock_given_vals, expected_out
    ):
        """
        Tests that parse_template_attrs method functions expectedly - with valid params
        should parse schema and given values and returns a list of attributes to map
        """
        res = self.instance._parse_template_attrs(
            template_name="mock-template",
            template_schema=mock_schema,
            given_vals=mock_given_vals,
        )
        self.assertEqual(res, expected_out)

    @parameterized.expand(
        [
            ("no default, no given value", {"attr1": None}, {}),
            ("no default, given value is None", {"attr1": None}, {"attr1": None}),
        ]
    )
    @raises(EmailTemplateError)
    def test_parse_template_attrs_invalid(self, _, mock_schema, mock_given_vals):
        """
        Tests that parse_template_attrs method functions expectedly - with invalid params
        should raise error if given_vals have missing required params
        """
        self.instance._parse_template_attrs(
            template_name="mock-template",
            template_schema=mock_schema,
            given_vals=mock_given_vals,
        )

    def test_get_template_file_valid(self):
        """
        Tests that get_template_file method functions expectedly - with valid filepath
        should open file at given filepath and return jinja template file
        """
        mock_template = NonCallableMock()
        mock_fp = "/path/to/file"
        self.mock_template_env.get_template.return_value = mock_template

        res = self.instance._get_template_file(mock_fp)
        self.mock_template_env.get_template.assert_called_once_with(mock_fp)
        self.assertEqual(res, mock_template)

    @raises(EmailTemplateError)
    def test_get_template_file_invalid(self):
        """
        Tests that get_template_file method functions expectedly - with invalid filepath
        should raise error if given an invalid filepath
        """
        self.mock_template_env.get_template.side_effect = TemplateNotFound(
            "template-error"
        )
        self.instance._get_template_file("invalid-path")

    def test_get_template_metadata_valid(self):
        """
        Tests that get_template_metadata method functions expectedly - with valid template name
        should get metadata info for a valid template name
        """
        res = self.instance._get_template_metadata(template_name="mock-template")
        self.assertEqual(res, self.mock_template_metadata["mock-template"])

    @raises(EmailTemplateError)
    def test_get_template_metadata_invalid(self):
        """
        Tests that get_template_metadata method functions expectedly - with invalid template name
        should raise error if given invalid template name
        """
        self.instance._get_template_metadata(template_name="an-invalid-template-name")

    @parameterized.expand(
        [
            (
                "html and schema",
                "mock-template",
                "html_filepath",
                {"attr1": "123", "attr2": "abc", "attr3": "def"},
            ),
            ("html and no schema", "mock-template-no-schema", "html_filepath", {}),
            (
                "plaintext and schema",
                "mock-template",
                "plaintext_filepath",
                {"attr1": "123", "attr2": "abc", "attr3": "def"},
            ),
            (
                "plaintext and no schema",
                "mock-template-no-schema",
                "plaintext_filepath",
                {},
            ),
        ]
    )
    @patch("email_api.template_handler.TemplateHandler._get_template_file")
    def test_render_template(
        self,
        _,
        mock_template_name,
        mock_file_path_key,
        mock_template_params,
        mock_get_template_file,
    ):
        """
        Tests that render_template method works expectedly
        Should call functions to get template, parse given attributes against metadata schema and
        render html version of template
        """
        mock_template_file = MagicMock()
        mock_get_template_file.return_value = mock_template_file

        mock_template_obj = MagicMock()
        mock_template_file.render.return_value = mock_template_obj

        res = self.instance._render_template(
            template_name=mock_template_name,
            file_path_key=mock_file_path_key,
            template_params=mock_template_params,
        )
        mock_get_template_file.assert_called_once_with(
            self.mock_template_metadata[mock_template_name][mock_file_path_key]
        )
        mock_template_file.render.assert_called_once_with(**mock_template_params)
        self.assertEqual(res, mock_template_obj)

    @parameterized.expand(
        [
            ("test missing html_filepath", "html_filepath"),
            ("test missing plaintext_filepath", "plaintext_filepath"),
        ]
    )
    @raises(EmailTemplateError)
    def test_render_template_missing_fp(self, _, file_path_key):
        """
        Tests that render_template method works expectedly - if metadata is missing config
        should raise error if necessary filepath config missing
        """
        self.instance._render_template(
            "mock-template-misconfigured", file_path_key=file_path_key
        )

    @raises(EmailTemplateError)
    def test_render_template_params_missing(self):
        """
        Tests that render_template method works expectedly - if template params missing when required
        should raise error if given a template which requires template params but none given
        """
        self.instance._render_template("mock-template", file_path_key="html_filepath")

    @raises(EmailTemplateError)
    @patch("email_api.template_handler.TemplateHandler._get_template_file")
    def test_render_template_jinja_failure(self, mock_get_template_file):
        """
        Tests that render_template method works expectedly - if jinja render() fails
        should raise EmailTemplate error
        """
        mock_get_template_file.return_value.render.side_effect = TemplateError()
        self.instance._render_template(
            "mock-template-no-schema",
            file_path_key="html_filepath",
        )

    @patch("email_api.template_handler.TemplateHandler._render_template")
    def test_render_html_template(self, mock_render_template):
        """
        Tests that render_html_template method works expectedly
        """
        res = self.instance.render_html_template(
            template_name="mock-template",
            template_params={"attr1": "123", "attr2": "abc", "attr3": "def"},
        )
        mock_render_template.assert_called_once_with(
            template_name="mock-template",
            file_path_key="html_filepath",
            template_params={"attr1": "123", "attr2": "abc", "attr3": "def"},
        )
        mock_render_template.return_value.replace.assert_called_once_with("\n", "")
        self.assertEqual(res, mock_render_template.return_value.replace.return_value)

    @patch("email_api.template_handler.TemplateHandler._render_template")
    def test_render_plaintext_template(self, mock_render_template):
        """
        Tests that render_plaintext_template method works expectedly
        """
        res = self.instance.render_plaintext_template(
            template_name="mock-template",
            template_params={"attr1": "123", "attr2": "abc", "attr3": "def"},
        )
        mock_render_template.assert_called_once_with(
            template_name="mock-template",
            file_path_key="plaintext_filepath",
            template_params={"attr1": "123", "attr2": "abc", "attr3": "def"},
        )
        self.assertEqual(res, mock_render_template.return_value)
