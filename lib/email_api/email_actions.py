from typing import Optional, List
from custom_types.email_api.aliases import (
    TemplateMappings,
    EmailAddress,
    EmailAddresses,
)

from structs.email_params import EmailParams
from structs.smtp_account import SMTPAccount

from email_api.emailer import Emailer

# pylint: disable=too-few-public-methods


class EmailActions:
    """
    Class that mirrors StackStorm ST2EmailActions. Each public method in this class can be used to handle jobs submitted
    via a StackStorm Action - this is done so that unittests can be written
    """

    @staticmethod
    def _setup_email_params(
        templates: TemplateMappings,
        subject: str,
        email_from: EmailAddress,
        email_cc: Optional[EmailAddresses] = None,
        attachment_filepaths: Optional[List[str]] = None,
    ):
        """
        static helper method to setup EmailParams dataclass from template mappings
        :param templates: A dictionary with template names as keys and a dictionary of schema args to replace as values
        :param: subject: (String): Subject of the email
        :param: email_from (String): Sender Email, subject (String): Email Subject,
        :param: email_cc (List[String]): Email addresses to Cc
        :param: attachment_filepaths (List[str]): filepaths to files to attach to email
        """
        return EmailParams.from_template_mappings(
            template_mappings=templates,
            subject=subject,
            email_from=email_from,
            email_cc=tuple(email_cc) if email_cc else None,
            attachment_filepaths=attachment_filepaths,
        )

    # pylint: disable=too-many-arguments
    def send_test_email(
        self,
        smtp_account: SMTPAccount,
        email_to: List[str],
        username: str,
        test_message: Optional[str] = None,
        as_html: bool = True,
        **kwargs
    ):
        """
        Action to send a test email using 'test' template.
        :param smtp_account: (SMTPAccount): SMTP config
        :param email_to: Email addresses to send the email to
        :param username: name required for test template
        :param test_message: message body required for test template
        :param as_html: send message body as html (if true) or plaintext (if false)
        :param kwargs: see EmailParams dataclass class docstring
        """
        email_params = self._setup_email_params(
            templates={
                "test": {"username": username, "test_message": test_message},
                "footer": {},
            },
            **kwargs
        )

        Emailer(smtp_account).send_email(
            email_to=tuple(email_to), email_params=email_params, as_html=as_html
        )
