from typing import Optional

from structs.email.smtp_account import SMTPAccount
from structs.email.email_template_details import EmailTemplateDetails
from structs.email.email_params import EmailParams

from email_api.emailer import Emailer


def send_test_email(
    smtp_account: SMTPAccount,
    username: str,
    test_message: Optional[str] = None,
    cc_cloud_support: bool = False,
    **kwargs
):
    """
    Method to send a test email using 'test' template - maps to email.test Action.
    :param smtp_account: (SMTPAccount): SMTP config
    :param username: name required for test template
    :param test_message: message body required for test template
    :param cc_cloud_support: whether to cc in cloud support
    :param kwargs: see EmailParams dataclass class docstring
    """

    if cc_cloud_support:
        email_cc = kwargs.get("email_cc", tuple())
        email_cc += ("cloud-support@stfc.ac.uk",)
        kwargs.update({"email_cc": email_cc})

    email_params = EmailParams.from_dict(
        {
            **{
                "email_templates": [
                    EmailTemplateDetails(
                        template_name="test",
                        template_params={
                            "username": username,
                            "test_message": test_message,
                        },
                    ),
                    EmailTemplateDetails(template_name="footer"),
                ]
            },
            **kwargs,
        }
    )

    Emailer(smtp_account).send_emails([email_params])
