from dataclasses import dataclass, fields
from typing import Optional, Dict, List
from custom_types.email_api.aliases import (
    TemplateMappings,
    EmailAddress,
    EmailAddresses,
)
from email_api.template_handler import TemplateHandler


@dataclass
# pylint:disable=too-many-instance-attributes
class EmailParams:
    """
    Email parameters that hold config info on how to structure and send an email
    :param: subject: (String): Subject of the email
    :param: email_from (String): Sender Email, subject (String): Email Subject,
    :param: email_cc (Tuple[String]): An Optional tuple of additional email addresses to Cc
    :param: body_html (String): Email body (HTML)
    :param: body_plaintext (String): Email body as plaintext
    :param: attachment_filepaths: List(Strings): An Optional list of filepaths to files to attach to email
        -must be relative filepaths which start from .../st2-cloud-pack/email_attachments
    """

    subject: str
    email_from: EmailAddress
    body_html: str
    body_plaintext: str
    email_cc: Optional[EmailAddresses] = None
    attachment_filepaths: Optional[List[str]] = None

    @staticmethod
    def from_dict(dictionary: Dict):
        """
        Method which returns instance of this dataclass from a dictionary (when creating from template mappings)
        :param dictionary: dictionary to use to instantiate dataclass
        """
        field_set = {field.name for field in fields(EmailParams) if field.init}
        filtered_arg_dict = {
            key: value for key, value in dictionary.items() if key in field_set
        }
        return EmailParams(**filtered_arg_dict)

    @staticmethod
    def from_template_mappings(template_mappings: TemplateMappings, **kwargs):
        """
        Method which creates instance of this dataclass - setting body_html and body_plaintext using
        a list of TemplateMappings.

        This method iteratively builds html and plaintext email body strings by taking a
        list of TemplateMappings. For each mapping in TemplateMappings, we read in the associated
        template file and convert it to string and concatenate - replacing keywords args with values given

        :param template_mappings: A dictionary with template names as keys and a dictionary of schema args
        to replace as values
        :param kwargs: All other values to populate EmailParams dataclass, see EmailParams class docstring
        """
        body_html = ""
        body_plaintext = ""

        template_handler = TemplateHandler()
        for template_name, template_params in template_mappings.items():
            body_html += template_handler.render_html_template(
                template_name=template_name,
                template_params=template_params,
            )

            body_plaintext += template_handler.render_plaintext_template(
                template_name=template_name,
                template_params=template_params,
            )

        kwargs.update({"body_html": body_html, "body_plaintext": body_plaintext})
        return EmailParams.from_dict(kwargs)
