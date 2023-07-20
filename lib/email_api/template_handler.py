import os

import jinja2
import yaml
from typing import Dict
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateError, TemplateNotFound
from exceptions.email_template_error import EmailTemplateError

# Holds relative filepath to email template metadata (from current dir)
EMAIL_TEMPLATE_METADATA_FP = "./email_templates.yaml"

# Holds relative filepath to root directory where email template files are stored (from current dir)
EMAIL_TEMPLATE_ROOT_DIR = "../../email_templates"


class TemplateHandler:
    """
    TemplateHandler class is used to get template files and render them using jinja2 templating engine.
    """

    def __init__(self):
        self._template_env = Environment(
            loader=FileSystemLoader(EMAIL_TEMPLATE_ROOT_DIR)
        )
        self._template_metadata = self._load_all_metadata()

    @staticmethod
    def _load_all_metadata() -> Dict:
        """
        Static method which reads in email templates yaml file. This file holds metadata for each template name.
        """
        with open(EMAIL_TEMPLATE_METADATA_FP, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise EmailTemplateError(
                    "could not load template metadata file"
                ) from exc

    @staticmethod
    def _parse_template_attrs(
        template_name: str, template_schema: Dict[str, str], given_vals: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Static method which returns values for all attributes to replace for the template that has been provided.
        attribute values either set to mapped values in 'given_vals' or set to a default given by 'template_schema'
        :param template_name: Name of the template
        :param template_schema: A dictionary holding required attribute names mapped to defaults
        :parma given_vals: A dictionary of given values - overrides defaults if mapping exists
        """
        given_vals = {key: val for key, val in given_vals.items() if val is not None}
        attrs = {
            key: given_vals.get(key, default)
            for default, key in template_schema.items()
        }
        missing_attrs = [key for key, val in attrs.items() if val is None]
        if missing_attrs:
            raise EmailTemplateError(
                f"Missing attributes required for template {template_name}: {', '.join(missing_attrs)}"
            )
        return attrs

    def _get_template_file(self, template_fp) -> jinja2.Template:
        """
        Method to read in template file as a jinja template from filepath.
        :param template_fp: a relative filepath for template file starting from 'EMAIL_TEMPLATE_ROOT_DIR'
        """
        try:
            return self._template_env.get_template(template_fp)
        except TemplateNotFound as not_found_exp:
            raise EmailTemplateError(
                "Could not find template with filepath "
                f"{os.path.join(EMAIL_TEMPLATE_METADATA_FP, template_fp)}"
            ) from not_found_exp

    def _get_template_metadata(self, template_name) -> Dict:
        """
        Method to get metadata values for a specific template from all metadata file
        :param template_name: name of template to get metadata for
        """
        metadata = self._template_metadata.get(template_name, None)
        if not metadata:
            raise EmailTemplateError(
                f"could not find template with name {template_name}, "
                f"make sure an entry in {EMAIL_TEMPLATE_METADATA_FP} exists"
            )
        return metadata

    def render_template(
        self, template_name: str, render_html: bool, template_params: Dict[str, str]
    ) -> str:
        """
        Public method to read email template from file, substitute given values from 'template_params' using jinja2 and
        return string
        :param template_name: name of template to render
        :param render_html: whether to render the html or plaintext version of the template
        :param template_params:
        """
        metadata = self._get_template_metadata(template_name)
        template_fp = (
            metadata["html_filepath"] if render_html else metadata["plaintext_filepath"]
        )
        template = self._get_template_file(template_fp)

        schema = metadata.get("schema", None)
        if schema and not template_params:
            raise EmailTemplateError(
                f"Template provided {template_name} requires following attributes, which are not given {list(schema.keys())}"
            )

        attrs = (
            self._parse_template_attrs(template_name, schema, template_params)
            if schema
            else {}
        )

        try:
            template_str = template.render(**attrs)
        except TemplateError as template_exp:
            raise EmailTemplateError(
                "Error occurred when rendering the template, check the template file "
                f"{os.path.join(EMAIL_TEMPLATE_METADATA_FP, template_fp)}"
            ) from template_exp

        if render_html:
            # remove erroneous newline values generated from template rendering
            template_str = template_str.replace("\n", "")
        return template_str
