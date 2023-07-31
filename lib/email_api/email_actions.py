from typing import Optional
from structs.email.email_params import EmailParams
from structs.email.email_template_details import EmailTemplateDetails
from structs.email.smtp_account import SMTPAccount

from email_api.emailer import Emailer

# pylint: disable=too-few-public-methods


class EmailActions:
    """
    Class that mirrors StackStorm ST2EmailActions. Each public method in this class is mapped to one or more StackStorm
    Action with the format 'email.*'
    """

    @staticmethod
    def _setup_email_params(**kwargs):
        """
        static helper method to setup EmailParams dataclass from template mappings.
        See EmailParams for all expected values
        """
        return EmailParams.from_dict(kwargs)

    # pylint: disable=too-many-arguments
    def send_test_email(
        self,
        smtp_account: SMTPAccount,
        username: str,
        test_message: Optional[str] = None,
        **kwargs
    ):
        """
        Method to send a test email using 'test' template - maps to email.test Action.
        :param smtp_account: (SMTPAccount): SMTP config
        :param username: name required for test template
        :param test_message: message body required for test template
        :param kwargs: see EmailParams dataclass class docstring
        """
        email_params = self._setup_email_params(
            email_templates=[
                EmailTemplateDetails(
                    template_name="test",
                    template_params={
                        "username": username,
                        "test_message": test_message,
                    },
                ),
                EmailTemplateDetails(template_name="footer"),
            ],
            **kwargs
        )

        Emailer(smtp_account).send_emails([email_params])
