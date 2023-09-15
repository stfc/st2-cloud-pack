from typing import Optional

from enums.query.query_presets import QueryPresetsGeneric
from structs.email.email_params import EmailParams
from structs.email.email_template_details import EmailTemplateDetails
from structs.email.smtp_account import SMTPAccount

from email_api.emailer import Emailer

from openstack_query.queries.server_query import ServerQuery
from enums.query.props.server_properties import ServerProperties

# pylint: disable=too-few-public-methods


class EmailActions:
    """
    Class that mirrors StackStorm ST2EmailActions. Each public method in this class is mapped to one or more StackStorm
    Action with the format 'email.*'
    """

    # pylint: disable=too-many-arguments
    def send_test_email(
        self,
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

    def get_shutoff_vms(self):
        """
        Method to get VMs which are in shutoff state
        Returns a list of shut off VMs with: server_id, server_id, server_status
        """
        select_server = [ServerProperties.from_string(prop) for prop in['server_id', 'server_name', 'server_status']]
        shutoff_query = ServerQuery.select(*select_server).where(EQUAL_TO, "server_status", "shutoff")
        sort_shutoff_query = shutoff_query.sort_by("server_name")
        q1 = sort_shutoff_query.run().to_list()
        return q1

    def convert_to_email_table(self):
        """
        Method to convert results of names of users and email addresses into an email table
        """
        pass

    def send_email_error(
        self,
        smtp_account: SMTPAccount,
        username: str,
        test_message: Optional[str] = None,
        cc_cloud_support: bool = False,
        **kwargs
    ):
        """
        Method to send email to user with VMs in 'error' state.
        """
        pass

    def send_email_shutoff(
            self,
            smtp_account: SMTPAccount,
            username: str,
            test_message: Optional[str] = None,
            cc_cloud_support: bool = False,
            **kwargs
    ):
        """
        Method to send email to user with VMs in 'shutoff' state.
        """
        pass
