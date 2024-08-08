from typing import Optional, Union

from email_api.emailer import Emailer
from enums.cloud_domains import CloudDomains
from enums.query.query_presets import QueryPresetsGeneric
from enums.query.props.hypervisor_properties import HypervisorProperties

from openstack_query import HypervisorQuery
from structs.email.email_params import EmailParams
from structs.email.email_template_details import EmailTemplateDetails
from structs.email.smtp_account import SMTPAccount


def find_down_hypervisors(cloud_account: str):
    """
    :param cloud_account: string represents cloud account to use
    """

    hypervisor_query_down = HypervisorQuery()
    hypervisor_query_down.where(
        QueryPresetsGeneric.ANY_IN,
        HypervisorProperties.HYPERVISOR_STATE,
        values=["down"],
    )
    hypervisor_query_down.run(
        cloud_account,
    )
    hypervisor_query_down.select(
        HypervisorProperties.HYPERVISOR_ID,
        HypervisorProperties.HYPERVISOR_NAME,
        HypervisorProperties.HYPERVISOR_STATE,
        HypervisorProperties.HYPERVISOR_STATUS,
    )

    if not hypervisor_query_down.to_props():
        raise RuntimeError("No hypervisors found in [DOWN] state")

    return hypervisor_query_down


def find_disabled_hypervisors(cloud_account: str):
    """
    :param cloud_account: string represents cloud account to use
    """

    hypervisor_query_disabled = HypervisorQuery()
    hypervisor_query_disabled.where(
        QueryPresetsGeneric.ANY_IN,
        HypervisorProperties.HYPERVISOR_STATUS,
        values=["disabled"],
    )
    hypervisor_query_disabled.run(
        cloud_account,
    )
    hypervisor_query_disabled.select(
        HypervisorProperties.HYPERVISOR_ID,
        HypervisorProperties.HYPERVISOR_NAME,
        HypervisorProperties.HYPERVISOR_STATE,
        HypervisorProperties.HYPERVISOR_STATUS,
    )

    if not hypervisor_query_disabled.to_props():
        raise RuntimeError("No hypervisors found with [DISABLED] status")

    return hypervisor_query_disabled


def print_email_params(
    email_addr: str, as_html: bool, down_table: str, disabled_table: str
):
    """
    Print email params instead of sending the email
    :param email_addr: email address to send to
    :param as_html: A boolean which if selected will send an email, otherwise prints email details only
    :param down_table: a table representing info found in openstack about HVs in down state
    :param disabled_table: a table representing info found in openstack about HVs in disabled status
    """
    print(
        f"Send Email To: {email_addr}\n"
        f"send as html: {as_html}\n"
        f"down hypervisors table:\n{down_table}\n"
        f"disabled hypervisors table:\n{disabled_table}\n"
    )


def build_email_params(down_table: str, disabled_table: str, **email_kwargs):
    """
    build email params dataclass which will be used to configure how to send the email
    :param down_table: a table representing info found in openstack about HVs in down state
    :param disabled_table: a table representing info found in openstack about HVs in disabled status
    :param email_kwargs: a set of email kwargs to pass to EmailParams
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
    Sends an email that shows the hypervisors in down state or have disabled status
    This email will contain 2 tables that show down state and disabled status
    :param smtp_account: (SMTPAccount): SMTP config
    :param cloud_account: string represents cloud account to use
    :param send_email: Actually send the email instead of printing what will be sent
    :param as_html: Send email as html
    :param use_override: flag if set will use override email address
    :param override_email_address: an overriding email address to use if override_email set
    :param cc_cloud_support: flag if set will cc cloud-support email address to each generated email
    :param email_params_kwargs: see EmailParams dataclass class docstring
    """

    hypervisor_query_down = find_down_hypervisors(cloud_account)
    hypervisor_query_disabled = find_disabled_hypervisors(cloud_account)

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
