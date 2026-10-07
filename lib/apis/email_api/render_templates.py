"""
Functions for loading and rendering Jinja2 email templates.

Template metadata is stored in file (``email_template_schemas.yaml``)
This file:
1. maps each email template to HTML and plaintext filepaths
2. provides a set of variables that can populate the template.
    - each variable is mapped to a default value (used if not given)
    - if default value is "null", the default value is "None"

The metadata file and template directory are resolved relative to this module:

Typical usage:
    details = EmailTemplateDetails("shutoff_vm", {"username": "alice", "shutoff_table": table})
    html_fragment = render_html_template(details)
    text_fragment = render_plaintext_template(details)
"""

import os
from pathlib import Path
from typing import Dict, Optional

from jinja2 import Environment, FileSystemLoader, Template
from jinja2.exceptions import TemplateError, TemplateNotFound
from yaml import YAMLError, safe_load

from apis.email_api.exceptions import EmailTemplateError
from apis.email_api.structs.email_template_details import EmailTemplateDetails

# Paths to the template metadata YAML file and root template directory.
EMAIL_TEMPLATE_METADATA_FP = Path(__file__).resolve().parent / "email_template_schemas.yaml"
EMAIL_TEMPLATE_ROOT_DIR = Path(__file__).resolve().parent / "templates"

# Module-level Jinja2 environment, initialised once on import.
_template_env = Environment(loader=FileSystemLoader(EMAIL_TEMPLATE_ROOT_DIR))


def _load_all_metadata(metadata_fp: Path) -> Dict:
    """
    Read and parse the template metadata YAML file.

    :params metadata_fp: Absolute path to the metadata YAML file.
    :returns: Parsed YAML contents as a dict.
    :raises EmailTemplateError: If the file cannot be read or parsed.
    """
    with open(metadata_fp, "r", encoding="utf-8") as stream:
        try:
            return safe_load(stream)
        except YAMLError as exc:
            raise EmailTemplateError("could not load template metadata file") from exc

# Template metadata is loaded from file into dict at import time
_template_metadata: Dict = _load_all_metadata(EMAIL_TEMPLATE_METADATA_FP)


def _get_template_file(template_fp: str) -> Template:
    """
    Load a Jinja2 template by its relative filepath.

    :params template_fp: Path relative to ``EMAIL_TEMPLATE_ROOT_DIR``.
    :returns: A compiled Jinja2 Template object.
    :raises EmailTemplateError: If the template file cannot be found.
    """
    try:
        return _template_env.get_template(template_fp)
    except TemplateNotFound as exc:
        raise EmailTemplateError(
            f"Could not find template file: {EMAIL_TEMPLATE_ROOT_DIR / template_fp}"
        ) from exc


def _get_template_metadata(template_name: str) -> Dict:
    """
    Return the metadata entry for a named template.

    :params template_name: The key to look up in ``email_template_schemas.yaml``.
    :returns: The metadata dict for the template (filepaths, schema, etc.).
    :raises EmailTemplateError: If no entry exists for ``template_name``.
    """
    metadata = _template_metadata.get(template_name)
    if not metadata:
        raise EmailTemplateError(
            f"could not find template with name '{template_name}', "
            f"make sure an entry in {EMAIL_TEMPLATE_METADATA_FP} exists"
        )
    return metadata


def _parse_template_attrs(
    template_details: EmailTemplateDetails, schema: Dict[str, Optional[str]]
) -> Dict[str, str]:
    """
    Resolve template variables against the schema, applying defaults.
    :params template_details: User-supplied template name and parameter values.
    :params schema: Mapping of variable name to default value
        (or ``None`` if the variable is mandatory with no default).
    :returns: A dict of resolved variable names to values, ready to pass to Jinja2.
    :raises EmailTemplateError: If any mandatory variable (default ``None``) is
            not provided in ``template_details.template_params``.
    """
    given = {
        k: v
        for k, v in (template_details.template_params or {}).items()
        if v is not None
    }
    attrs = {key: given.get(key, default) for key, default in schema.items()}

    missing = [k for k, v in attrs.items() if v is None]
    if missing:
        raise EmailTemplateError(
            f"Missing required attributes for template "
            f"'{template_details.template_name}': {', '.join(missing)}"
        )
    return attrs


def _render_template(template_details: EmailTemplateDetails, file_path_key: str) -> str:
    """
    Render a template identified by name and format key.

    :params template_details: Template name and parameter values supplied by the caller.
    :params file_path_key: The metadata key that holds the filepath for this
            format, either ``"html_filepath"`` or ``"plaintext_filepath"``.
    :returns: The rendered template as a string.
    :raises EmailTemplateError: If metadata is missing the filepath key, required
            variables are absent, or Jinja2 raises a render error.
    """
    metadata = _get_template_metadata(template_details.template_name)

    try:
        template_fp = metadata[file_path_key]
    except KeyError as exc:
        raise EmailTemplateError(
            f"Template '{template_details.template_name}' metadata is missing "
            f"'{file_path_key}' entry"
        ) from exc

    template = _get_template_file(template_fp)
    schema = metadata.get("schema")

    if schema and not template_details.template_params:
        raise EmailTemplateError(
            f"Template '{template_details.template_name}' requires attributes: "
            f"{list(schema.keys())}"
        )

    attrs = _parse_template_attrs(template_details, schema) if schema else {}

    try:
        return template.render(**attrs)
    except TemplateError as exc:
        raise EmailTemplateError(
            f"Error rendering template '{template_details.template_name}' "
            f"({os.path.join(EMAIL_TEMPLATE_ROOT_DIR, template_fp)})"
        ) from exc


def render_html_template(template_details: EmailTemplateDetails) -> str:
    """
    Render the HTML variant of a template and strip newlines.

    Newlines are stripped as HTML email clients render them as "/n" in the body of the email

    :params template_details: Template name and parameter values.
    :returns: The rendered HTML string with newlines removed.
    :raises EmailTemplateError: See :func:`_render_template`.
    """
    return _render_template(template_details, "html_filepath").replace("\n", "")


def render_plaintext_template(template_details: EmailTemplateDetails) -> str:
    """
    Render the plaintext variant of a template.

    :params template_details: Template name and parameter values.
    :returns: The rendered plaintext string.
    :raises EmailTemplateError: See :func:`_render_template`.
    """
    return _render_template(template_details, "plaintext_filepath")