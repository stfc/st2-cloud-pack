from dataclasses import dataclass, fields
from typing import Optional, Dict, List
from custom_types.email_api.aliases import (
    EmailAddress,
    EmailAddresses,
)
from structs.email.email_template_details import EmailTemplateDetails


@dataclass
# pylint:disable=too-many-instance-attributes
class EmailParams:
    """
    Email parameters that hold config info on how to structure and send an email
    :param subject: (String): Subject of the email
    :param email_from: (String): Sender Email, subject (String): Email Subject,
    :param email_cc: (Tuple[String]): An Optional tuple of additional email addresses to Cc
    :param email_templates: List(TemplateDetails): A list of templates to render - as TemplateDetail dataclass
    :param as_html: bool: True if email templates should be rendered as html or not
    :param attachment_filepaths: List(Strings): An Optional list of filepaths to files to attach to email
        -must be relative filepaths which start from .../st2-cloud-pack/email_attachments
    """

    subject: str
    email_from: EmailAddress
    email_to: EmailAddresses
    email_templates: List[EmailTemplateDetails]
    as_html: bool = True
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
