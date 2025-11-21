from typing import Optional, Union

from apis.openstack_api.enums.cloud_domains import CloudDomains
from apis.email_api.structs.email_params import EmailParams
from apis.email_api.structs.email_template_details import EmailTemplateDetails
from apis.email_api.structs.smtp_account import SMTPAccount
from apis.email_api.emailer import Emailer
from apis.openstack_query_api.hypervisor_queries import (
    find_down_hypervisors,
    find_disabled_hypervisors,
)


def print_email_params(
    email_addr: str, as_html: bool, down_table: str, disabled_table: str
):
    """
    Print email params instead of sending the email.
    :param email_addr: The email address to send to
    :param as_html: A boolean which, if True, will send an email - otherwise, prints email details only
    :param down_table: A table representing info found in OpenStack about HVs in down state
    :param disabled_table: A table representing info found in OpenStack about HVs in disabled status
    """
    print(
        f"Send Email To: {email_addr}\n"
        f"send as html: {as_html}\n"
        f"down hypervisors table:\n{down_table}\n"
        f"disabled hypervisors table:\n{disabled_table}\n"
    )


def build_email_params(down_table: str, disabled_table: str, **email_kwargs):
    """
    Build email params dataclass which will be used to configure how to send the email.
    :param down_table: A table representing info found in OpenStack about HVs in down state
    :param disabled_table: A table representing info found in OpenStack about HVs in disabled status
    :param email_kwargs: A set of email kwargs to pass to EmailParams
    """
    body = EmailTemplateDetails(
        template_name="hypervisor_down_disabled",
        template_params={
            "down_table": down_table,
            "disabled_table": disabled_table,
        },
    )

    footer = EmailTemplateDetails(template_name="footer", template_params={})

    return EmailParams(email_templates=[body, footer], **email_kwargs)


# pylint:disable=too-many-arguments
# pylint:disable=too-many-locals
def send_down_disabled_hypervisors_email(
    smtp_account: SMTPAccount,
    cloud_account: Union[CloudDomains, str],
    as_html: bool = False,
    send_email: bool = False,
    use_override: bool = False,
    override_email_address: Optional[str] = "cloud-support@stfc.ac.uk",
    cc_cloud_support: bool = False,
    **email_params_kwargs,
):
    """
    Sends an email that shows the hypervisors in down state or have disabled status.
    This email will contain 2 tables, showing down state and disabled status.
    :param smtp_account: (SMTPAccount): SMTP config
    :param cloud_account: A string representing the cloud account to use
    :param send_email: A boolean which, if True, will send the email instead of printing what will be sent
    :param as_html: A boolean which, if True, will send the email as html
    :param use_override: A boolean which, if True, will use the override email address
    :param override_email_address: A string representing the overriding email address to use if override_email is True
    :param cc_cloud_support: A boolean which, if True, will cc the cloud-support email address to each generated email
    :param email_params_kwargs: See EmailParams dataclass class docstring
    """

    hypervisor_query_down = find_down_hypervisors(cloud_account)
    if not hypervisor_query_down.to_props():
        raise RuntimeError("No hypervisors found in [DOWN] state")

    hypervisor_query_disabled = find_disabled_hypervisors(cloud_account)
    if not hypervisor_query_disabled.to_props():
        raise RuntimeError("No hypervisors found with [DISABLED] status")

    send_to = ["ops-team"]
    if use_override:
        send_to = [override_email_address]

    if as_html:
        down_hv_list = hypervisor_query_down.to_html()
        disabled_hv_list = hypervisor_query_disabled.to_html()
    else:
        down_hv_list = hypervisor_query_down.to_string()
        disabled_hv_list = hypervisor_query_disabled.to_string()

    if not send_email:
        print_email_params(send_to[0], as_html, down_hv_list, disabled_hv_list)
        return

    email_params = build_email_params(
        down_hv_list,
        disabled_hv_list,
        email_to=send_to,
        as_html=as_html,
        email_cc=("cloud-support@stfc.ac.uk",) if cc_cloud_support else None,
        **email_params_kwargs,
    )
    Emailer(smtp_account).send_emails([email_params])
