from typing import List, Optional, Union

from apis.openstack_api.enums.cloud_domains import CloudDomains

from apis.email_api.structs.email_params import EmailParams
from apis.email_api.structs.email_template_details import EmailTemplateDetails
from apis.email_api.structs.smtp_account import SMTPAccount
from apis.email_api.emailer import Emailer
from apis.openstack_query_api.server_queries import (
    find_shutoff_servers,
    group_servers_by_user_id,
)
from apis.openstack_query_api.user_queries import find_user_info


def print_email_params(
    email_addr: str,
    user_name: str,
    as_html: bool,
    shutoff_table: str,
    days_threshold: int,
):
    """
    Prints email params instead of sending the email.
    :param email_addr: Email address to send to
    :param user_name: Name of user in OpenStack
    :param as_html: A boolean which if selected will send an email, otherwise prints email details only
    :param shutoff_table: A table representing info found in OpenStack about VMs in shutoff state
    :param days_threshold: An integer which specifies the minimum age (in days) of the servers to be found
    """
    print(
        f"Send Email To: {email_addr}\n"
        f"email_templates shutoff-email: username {user_name}\n"
        f"send as html: {as_html}\n"
        f"shutoff table: {shutoff_table}\n"
        f"days threshold: {days_threshold}\n"
    )


def build_email_params(
    user_name: str, shutoff_table: str, days_threshold: int, **email_kwargs
):
    """
    Builds email params dataclass which will be used to configure how to send the email.
    :param user_name: Name of user in OpenStack
    :param shutoff_table: A table representing info found in OpenStack about VMs that are in shutoff state
    :param email_kwargs: A set of email kwargs to pass to EmailParams
    """
    body = EmailTemplateDetails(
        template_name="shutoff_vm",
        template_params={
            "username": user_name,
            "shutoff_table": shutoff_table,
            "days_threshold": days_threshold,
        },
    )

    footer = EmailTemplateDetails(template_name="footer", template_params={})

    return EmailParams(email_templates=[body, footer], **email_kwargs)


# pylint:disable=too-many-arguments
# pylint:disable=too-many-locals
def send_shutoff_vm_email(
    smtp_account: SMTPAccount,
    cloud_account: Union[CloudDomains, str],
    limit_by_projects: Optional[List[str]] = None,
    days_threshold: int = 0,
    all_projects: bool = False,
    as_html: bool = False,
    send_email: bool = False,
    use_override: bool = False,
    override_email_address: Optional[str] = "cloud-support@stfc.ac.uk",
    cc_cloud_support: bool = False,
    **email_params_kwargs,
):
    """
    Sends an email to each user who owns one or more VMs that are in shutoff state.
    This email will contain a notice to delete or rebuild the VM.
    :param smtp_account: (SMTPAccount): SMTP config
    :param cloud_account: String representing the cloud account to use
    :param limit_by_projects: A list of project names or ids to limit search in
    :param days_threshold: An integer which specifies the minimum age (in days) of the servers to be found
    :param all_projects: A boolean which, if True, will search in all projects
    :param send_email: A boolean which, if True, will send the email instead of printing what will be sent
    :param as_html: A boolean which, if True, will send the email as html
    :param use_override: A boolean which, if True, will use the override email address
    :param override_email_address: An overriding email address to use if override_email set
    :param cc_cloud_support: A boolean which, if True, will cc cloud-support email address to each generated email
    :param email_params_kwargs: See EmailParams dataclass class docstring
    """
    if limit_by_projects and all_projects:
        raise RuntimeError(
            "given both project list and all_projects flag - please choose only one"
        )
    if not (limit_by_projects or all_projects):
        raise RuntimeError(
            "please provide either a list of project identifiers or with flag 'all_projects' to run globally"
        )

    server_query = find_shutoff_servers(
        cloud_account, days_threshold, limit_by_projects
    )

    if not server_query.to_props():
        raise RuntimeError(
            f"No servers found in [SHUTOFF] state on projects "
            f"{','.join(limit_by_projects) if limit_by_projects else '[all projects]'}"
        )

    grouped_query = group_servers_by_user_id(server_query)

    for user_id in grouped_query.to_props().keys():
        user_name, email_addr = find_user_info(
            user_id, cloud_account, override_email_address
        )
        send_to = [email_addr]
        if use_override:
            send_to = [override_email_address]

        if as_html:
            server_list = grouped_query.to_html(
                groups=[user_id], include_group_titles=False
            )
        else:
            server_list = grouped_query.to_string(
                groups=[user_id], include_group_titles=False
            )

        if not send_email:
            print_email_params(
                send_to[0], user_name, as_html, server_list, days_threshold
            )
            continue

        email_params = build_email_params(
            user_name,
            server_list,
            email_to=send_to,
            as_html=as_html,
            days_threshold=days_threshold,
            email_cc=("cloud-support@stfc.ac.uk",) if cc_cloud_support else None,
            **email_params_kwargs,
        )
        Emailer(smtp_account).send_emails([email_params])
