from typing import Optional
from custom_types.email_api.aliases import (
    TemplateMappings,
    EmailAddressList,
    EmailAddress,
)

from structs.email_params import EmailParams
from structs.smtp_account import SMTPAccount

from email_api.emailer import Emailer


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
        send_as_html: bool = True,
        email_cc: Optional[EmailAddressList] = None,
        test_override_email: Optional[str] = None,
    ):
        """
        static helper method to setup EmailParams dataclass from template mappings
        :param templates: A dictionary with template names as keys and a dictionary of schema args to replace as values
        :param: subject: (String): Subject of the email
        :param: email_from (String): Sender Email, subject (String): Email Subject,
        :param: email_cc (List[String]): Email addresses to Cc
        :param: send_as_html (Boolean): a flag to set body as html or plaintext
        :param test_override_email Optional(String): an override email to send all emails to - for testing purposes
        """
        return EmailParams.from_template_mappings(
            template_mappings=templates,
            subject=subject,
            email_from=email_from,
            email_cc=email_cc,
            send_as_html=send_as_html,
            test_override_email=test_override_email,
        )

    def send_test_email(
        self,
        smtp_account: SMTPAccount,
        email_to: EmailAddressList,
        username: str,
        test_message: Optional[str] = None,
        **kwargs
    ):
        """
        Action to send a test email using 'test' template.
        :param smtp_account: (SMTPAccount): SMTP config
        :param email_to: Email addresses to send the email to
        :param username: user name required for test template
        :param test_message: message body required for test template
        :param kwargs: see EmailParams dataclass class docstring
        """
        email_params = self._setup_email_params(
            templates={"test": {"username": username, "test_message": test_message}},
            **kwargs
        )

        Emailer(smtp_account).send_email(email_to=email_to, email_params=email_params)
