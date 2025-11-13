from typing import List, Optional, Union

from openstackquery import UserQuery

from apis.openstack_api.enums.cloud_domains import CloudDomains

from apis.email_api.structs.email_params import EmailParams
from apis.email_api.structs.email_template_details import EmailTemplateDetails
from apis.email_api.structs.smtp_account import SMTPAccount
from apis.email_api.emailer import Emailer
from apis.openstack_query_api.server_queries import (
    find_shutoff_servers,
    group_servers_by_user_id,
)


def print_email_params(
    email_addr: str, user_name: str, as_html: bool, shutoff_table: str
):
    """
    Print email params instead of sending the email
    :param email_addr: email address to send to
    :param user_name: name of user in openstack
    :param as_html: A boolean which if selected will send an email, otherwise prints email details only
    :param shutoff_table: a table representing info found in openstack
    about VMs in shutoff state
    """
    print(
        f"Send Email To: {email_addr}\n"
        f"email_templates shutoff-email: username {user_name}\n"
        f"send as html: {as_html}\n"
        f"shutoff table: {shutoff_table}\n"
    )


def build_email_params(user_name: str, shutoff_table: str, **email_kwargs):
    """
    build email params dataclass which will be used to configure how to send the email
    :param user_name: name of user in openstack
    :param shutoff_table: a table representing info found in openstack about VMs
        that are in shutoff state
    :param email_kwargs: a set of email kwargs to pass to EmailParams
    """
    body = EmailTemplateDetails(
        template_name="shutoff_vm",
        template_params={
            "username": user_name,
            "shutoff_table": shutoff_table,
        },
    )

    footer = EmailTemplateDetails(template_name="footer", template_params={})

    return EmailParams(email_templates=[body, footer], **email_kwargs)


def find_user_info(user_id, cloud_account, override_email_address):
    """
    run a UserQuery to find the email address and username associated for a user id.
    :param user_id: the openstack user id to find email address for
    :param cloud_account: string represents cloud account to use
    :param override_email_address: email address to return if no email address found via UserQuery
    """
    user_query = UserQuery()
    user_query.select("name", "email_address")
    user_query.where("equal_to", "id", value=user_id)
    user_query.run(cloud_account=cloud_account)
    res = user_query.to_props(flatten=True)
    if not res or not res["user_email"][0]:
        return "", override_email_address
    return res["user_name"][0], res["user_email"][0]


# pylint:disable=too-many-arguments
# pylint:disable=too-many-locals
def send_shutoff_vm_email(
    smtp_account: SMTPAccount,
    cloud_account: Union[CloudDomains, str],
    limit_by_projects: Optional[List[str]] = None,
    all_projects: bool = False,
    as_html: bool = False,
    send_email: bool = False,
    use_override: bool = False,
    override_email_address: Optional[str] = "cloud-support@stfc.ac.uk",
    cc_cloud_support: bool = False,
    **email_params_kwargs,
):
    """
    Sends an email to each user who owns one or more VMs that are in shutoff state
    This email will contain a notice to delete or rebuild the VM
    :param smtp_account: (SMTPAccount): SMTP config
    :param cloud_account: string represents cloud account to use
    :param limit_by_projects: A list of project names or ids to limit search in
    :param all_projects: A boolean which if selected will search in all projects
    :param send_email: Actually send the email instead of printing what will be sent
    :param as_html: Send email as html
    :param use_override: flag if set will use override email address
    :param override_email_address: an overriding email address to use if override_email set
    :param cc_cloud_support: flag if set will cc cloud-support email address to each generated email
    :param email_params_kwargs: see EmailParams dataclass class docstring
    """
    if limit_by_projects and all_projects:
        raise RuntimeError(
            "given both project list and all_projects flag - please choose only one"
        )
    if not (limit_by_projects or all_projects):
        raise RuntimeError(
            "please provide either a list of project identifiers or with flag 'all_projects' to run globally"
        )

    server_query = find_shutoff_servers(cloud_account, limit_by_projects)

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
            print_email_params(send_to[0], user_name, as_html, server_list)
            continue

        email_params = build_email_params(
            user_name,
            server_list,
            email_to=send_to,
            as_html=as_html,
            email_cc=("cloud-support@stfc.ac.uk",) if cc_cloud_support else None,
            **email_params_kwargs,
        )
        Emailer(smtp_account).send_emails([email_params])
