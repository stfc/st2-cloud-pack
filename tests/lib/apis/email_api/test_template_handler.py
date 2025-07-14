from unittest.mock import patch, mock_open, NonCallableMock, MagicMock

import pytest
from yaml import YAMLError


from jinja2.exceptions import TemplateError, TemplateNotFound
from apis.email_api.exceptions.email_template_error import EmailTemplateError
from apis.email_api.template_handler import TemplateHandler
from apis.email_api.structs.email_template_details import EmailTemplateDetails

# pylint:disable=protected-access


@pytest.fixture(name="mock_template_metadata", scope="module")
def mock_template_metadata_fixture():
    """
    Returns a mock template metadata dict for the email API to use
    """
    return {
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


@pytest.fixture(name="instance")
def instance_fixture(mock_template_metadata):
    """
    Returns a template parsing instance with the mock template metadata
    injected for testing
    """
    instance = TemplateHandler(mock_template_metadata)
    instance._template_env = MagicMock()
    return instance


@patch("apis.email_api.template_handler.safe_load")
@patch("builtins.open", new_callable=mock_open)
def test_load_all_metadata_valid(mock_file, mock_yaml_load, instance):
    """
    Test that load_all_metadata method functions expectedly
    Reads yaml file containing metadata info set in EMAIL_TEMPLATE_METADATA_FP
    """
    safe_load_out = NonCallableMock()
    mock_yaml_load.return_value = safe_load_out

    res = instance._load_all_metadata("some-fp")
    mock_file.assert_called_once_with("some-fp", "r", encoding="utf-8")
    mock_yaml_load.assert_called_once_with(mock_file.return_value)
    assert res == safe_load_out


@patch("apis.email_api.template_handler.safe_load")
@patch("builtins.open", new_callable=mock_open)
def test_load_all_metadata_invalid(_, mock_yaml_load, instance):
    """
    Tests that load_all_metadata method functions expectedly
    Raises error if yaml file cannot be read
    """

    mock_yaml_load.side_effect = YAMLError()
    with pytest.raises(EmailTemplateError):
        instance._load_all_metadata("some-fp")


@pytest.mark.parametrize(
    "mock_schema, mock_given_vals, expected_out",
    [
        (
            # "with emtpy given vals, use defaults",
            {"attr1": "def1", "attr2": "def2", "attr3": "def3"},
            {},
            {"attr1": "def1", "attr2": "def2", "attr3": "def3"},
        ),
        (
            # "with given vals and defaults, use given vals",
            {"attr1": "def1", "attr2": "def2", "attr3": "def3"},
            {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
            {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
        ),
        (
            # "with given vals and no defaults, use given vals",
            {"attr1": None, "attr2": None, "attr3": None},
            {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
            {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
        ),
        (
            # "with given vals set as None, use defaults",
            {"attr1": None, "attr2": None, "attr3": None},
            {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
            {"attr1": "val1", "attr2": "val2", "attr3": "val3"},
        ),
        (
            # "mix of given vals and defaults, use given vals if available else defaults",
            {"attr1": None, "attr2": "def2", "attr3": "def3"},
            {"attr1": "val1", "attr2": None},
            {"attr1": "val1", "attr2": "def2", "attr3": "def3"},
        ),
    ],
)
def test_parse_template_attrs_valid(
    instance, mock_schema, mock_given_vals, expected_out
):
    """
    Tests that parse_template_attrs method functions expectedly - with valid params
    should parse schema and given values and returns a list of attributes to map
    """
    res = instance._parse_template_attrs(
        EmailTemplateDetails(
            template_name="mock-template", template_params=mock_given_vals
        ),
        template_schema=mock_schema,
    )
    assert res == expected_out


@pytest.mark.parametrize(
    "mock_schema, mock_given_vals",
    [
        # no default, no given value
        ({"attr1": None}, {}),
        # no default, given value is None
        ({"attr1": None}, {"attr1": None}),
    ],
)
def test_parse_template_attrs_invalid(mock_schema, mock_given_vals, instance):
    """
    Tests that parse_template_attrs method functions expectedly - with invalid params
    should raise error if given_vals have missing required params
    """
    with pytest.raises(EmailTemplateError):
        instance._parse_template_attrs(
            EmailTemplateDetails(
                template_name="mock-template", template_params=mock_given_vals
            ),
            template_schema=mock_schema,
        )


def test_get_template_file_valid(instance):
    """
    Tests that get_template_file method functions expectedly - with valid filepath
    should open file at given filepath and return jinja template file
    """
    mock_template_env = MagicMock()
    instance._template_env = mock_template_env

    mock_template = NonCallableMock()
    mock_fp = "/path/to/file"
    mock_template_env.get_template.return_value = mock_template

    res = instance._get_template_file(mock_fp)
    mock_template_env.get_template.assert_called_once_with(mock_fp)
    assert res == mock_template


def test_get_template_file_invalid(instance):
    """
    Tests that get_template_file method functions expectedly - with invalid filepath
    should raise error if given an invalid filepath
    """
    mock_template_env = MagicMock()
    instance._template_env = mock_template_env

    mock_template_env.get_template.side_effect = TemplateNotFound("template-error")
    with pytest.raises(EmailTemplateError):
        instance._get_template_file("invalid-path")


def test_get_template_metadata_valid(instance, mock_template_metadata):
    """
    Tests that get_template_metadata method functions expectedly - with valid template name
    should get metadata info for a valid template name
    """
    res = instance._get_template_metadata(template_name="mock-template")
    assert res == mock_template_metadata["mock-template"]


def test_get_template_metadata_invalid(instance):
    """
    Tests that get_template_metadata method functions expectedly - with invalid template name
    should raise error if given invalid template name
    """
    with pytest.raises(EmailTemplateError):
        instance._get_template_metadata(template_name="an-invalid-template-name")


@pytest.mark.parametrize(
    "mock_template_name, mock_file_path_key, mock_template_params",
    [
        # "html and schema",
        (
            "mock-template",
            "html_filepath",
            {"attr1": "123", "attr2": "abc", "attr3": "def"},
        ),
        # "html and no schema"
        ("mock-template-no-schema", "html_filepath", {}),
        # "plaintext and schema",
        (
            "mock-template",
            "plaintext_filepath",
            {"attr1": "123", "attr2": "abc", "attr3": "def"},
        ),
        # "plaintext and no schema",
        (
            "mock-template-no-schema",
            "plaintext_filepath",
            {},
        ),
    ],
)
@patch("apis.email_api.template_handler.TemplateHandler._get_template_file")
# pylint:disable=too-many-arguments
def test_render_template(
    mock_get_template_file,
    mock_template_name,
    mock_file_path_key,
    mock_template_params,
    instance,
    mock_template_metadata,
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

    res = instance._render_template(
        template_details=EmailTemplateDetails(
            template_name=mock_template_name, template_params=mock_template_params
        ),
        file_path_key=mock_file_path_key,
    )
    mock_get_template_file.assert_called_once_with(
        mock_template_metadata[mock_template_name][mock_file_path_key]
    )
    mock_template_file.render.assert_called_once_with(**mock_template_params)
    assert res == mock_template_obj


@pytest.mark.parametrize("file_path_key", ["html_filepath", "plaintext_filepath"])
def test_render_template_missing_fp(file_path_key, instance):
    """
    Tests that render_template method works expectedly - if metadata is missing config
    should raise error if necessary filepath config missing
    """
    with pytest.raises(EmailTemplateError):
        instance._render_template(
            template_details=EmailTemplateDetails(
                template_name="mock-template-misconfigured"
            ),
            file_path_key=file_path_key,
        )


def test_render_template_params_missing(instance):
    """
    Tests that render_template method works expectedly - if template params missing when required
    should raise error if given a template which requires template params but none given
    """
    with pytest.raises(EmailTemplateError):
        instance._render_template(
            template_details=EmailTemplateDetails(
                template_name="mock-template-misconfigured"
            ),
            file_path_key="html_filepath",
        )


@patch("apis.email_api.template_handler.TemplateHandler._get_template_file")
def test_render_template_jinja_failure(mock_get_template_file, instance):
    """
    Tests that render_template method works expectedly - if jinja render() fails
    should raise EmailTemplate error
    """
    mock_get_template_file.return_value.render.side_effect = TemplateError()
    with pytest.raises(EmailTemplateError):
        instance._render_template(
            template_details=EmailTemplateDetails(
                template_name="mock-template-no-schema",
            ),
            file_path_key="html_filepath",
        )


@patch("apis.email_api.template_handler.TemplateHandler._render_template")
def test_render_html_template(mock_render_template, instance):
    """
    Tests that render_html_template method works expectedly
    """
    mock_template_details = EmailTemplateDetails(
        template_name="mock-template",
        template_params={"attr1": "123", "attr2": "abc", "attr3": "def"},
    )
    res = instance.render_html_template(mock_template_details)
    mock_render_template.assert_called_once_with(
        template_details=mock_template_details,
        file_path_key="html_filepath",
    )
    mock_render_template.return_value.replace.assert_called_once_with("\n", "")
    assert res == mock_render_template.return_value.replace.return_value


@patch("apis.email_api.template_handler.TemplateHandler._render_template")
def test_render_plaintext_template(mock_render_template, instance):
    """
    Tests that render_plaintext_template method works expectedly
    """
    mock_template_details = EmailTemplateDetails(
        template_name="mock-template",
        template_params={"attr1": "123", "attr2": "abc", "attr3": "def"},
    )

    res = instance.render_plaintext_template(mock_template_details)

    mock_render_template.assert_called_once_with(
        template_details=mock_template_details,
        file_path_key="plaintext_filepath",
    )
    assert res == mock_render_template.return_value
