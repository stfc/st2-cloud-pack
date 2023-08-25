import os
from typing import Dict
from pathlib import Path

from yaml import safe_load, YAMLError
from jinja2 import Environment, FileSystemLoader, Template
from jinja2.exceptions import TemplateError, TemplateNotFound
from exceptions.email_template_error import EmailTemplateError

from structs.email.email_template_details import EmailTemplateDetails


class TemplateHandler:
    """
    TemplateHandler class is used to get template files and render them using jinja2 templating engine.
    An email body is a string made up of one or more rendered jinja2 templates.
    """

    # Holds absolute filepath to email template metadata (from current dir)
    # .../st2-cloud-pack/lib/email_api/email_templates.yaml
    EMAIL_TEMPLATE_METADATA_FP = (
        Path(__file__).resolve().parent / "email_template_schemas.yaml"
    )

    # Holds absolute dirpath to directory where email template files are stores
    # .../st2-cloud-pack/email_templates
    EMAIL_TEMPLATE_ROOT_DIR = (
        Path(__file__).resolve().parent.parent.parent / "email_templates"
    )

    def __init__(self, template_metadata=None):
        self._template_env = Environment(
            loader=FileSystemLoader(self.EMAIL_TEMPLATE_ROOT_DIR)
        )

        self._template_metadata = (
            template_metadata
            if template_metadata
            else self._load_all_metadata(self.EMAIL_TEMPLATE_METADATA_FP)
        )

    @staticmethod
    def _load_all_metadata(metadata_fp) -> Dict:
        """
        Method which reads in email templates yaml file. This file holds metadata for each template name.
        """
        with open(metadata_fp, "r", encoding="utf-8") as stream:
            try:
                return safe_load(stream)
            except YAMLError as exc:
                raise EmailTemplateError(
                    "could not load template metadata file"
                ) from exc

    @staticmethod
    def _parse_template_attrs(
        template_details: EmailTemplateDetails, template_schema: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Static method which returns values for all attributes to replace for the template that has been provided.
        attribute values either set to mapped values in 'given_vals' or set to a default given by 'template_schema'
        :param template_details: A dataclass containing info on templates
        :param template_schema: A dictionary holding required attribute names mapped to defaults
        """
        template_params = {}
        if template_details.template_params:
            template_params = template_details.template_params

        given_vals = {
            key: val for key, val in template_params.items() if val is not None
        }
        attrs = {
            key: given_vals.get(key, default)
            for key, default in template_schema.items()
        }

        missing_attrs = [key for key, val in attrs.items() if val is None]
        if missing_attrs:
            raise EmailTemplateError(
                f"Missing attributes required for template {template_details.template_name}: {', '.join(missing_attrs)}"
            )

        return attrs

    def _get_template_file(self, template_fp) -> Template:
        """
        Method to read in template file as a jinja template from filepath.
        :param template_fp: a relative filepath for template file starting from 'EMAIL_TEMPLATE_ROOT_DIR'
        """
        try:
            return self._template_env.get_template(template_fp)
        except TemplateNotFound as not_found_exp:
            raise EmailTemplateError(
                "Could not find template with filepath {self.EMAIL_TEMPLATE_ROOT_DIR / template_fp}"
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
                f"make sure an entry in {self.EMAIL_TEMPLATE_METADATA_FP} exists"
            )
        return metadata

    def render_html_template(self, template_details: EmailTemplateDetails):
        """
        Method to get html email template, substitute given values from 'template_params' using jinja2 and return
        a rendered string
        :param template_details: dataclass representing user-defined values for template
        """

        return self._render_template(
            template_details=template_details,
            file_path_key="html_filepath",
        ).replace("\n", "")

    def render_plaintext_template(self, template_details: EmailTemplateDetails):
        """
        Method to get plaintext email template, substitute given values from 'template_params' using jinja2 and return
        a rendered string
        :param template_details: dataclass representing user-defined values for template
        """
        return self._render_template(
            template_details=template_details,
            file_path_key="plaintext_filepath",
        )

    def _render_template(
        self,
        template_details: EmailTemplateDetails,
        file_path_key: str,
    ) -> str:
        """
        Helper method to render template
        :param template_details: dataclass representing user-defined values for template
        :param file_path_key: metadata dictionary key which holds the filepath pointing to template file
        """
        metadata = self._get_template_metadata(template_details.template_name)
        try:
            template_fp = metadata[file_path_key]
        except KeyError as exp:
            raise EmailTemplateError(
                f"Template {template_details.template_name} metadata is missing {file_path_key} entry"
            ) from exp

        template = self._get_template_file(template_fp)
        schema = metadata.get("schema", None)
        if schema and not template_details.template_params:
            raise EmailTemplateError(
                f"Template provided {template_details.template_name} "
                f"requires following attributes: {list(schema.keys())}"
            )

        attrs = {}
        if schema:
            attrs = self._parse_template_attrs(template_details, schema)

        try:
            return template.render(**attrs)
        except TemplateError as template_exp:
            raise EmailTemplateError(
                "Error occurred when rendering the template, check the template file "
                f"{os.path.join(self.EMAIL_TEMPLATE_METADATA_FP, template_fp)}"
            ) from template_exp
