from datetime import datetime
from typing import List, Optional, Union
from apis.email_api.emailer import Emailer
from apis.email_api.structs.email_params import EmailParams
from apis.email_api.structs.email_template_details import EmailTemplateDetails
from apis.email_api.structs.smtp_account import SMTPAccount
from apis.openstack_api.enums.cloud_domains import CloudDomains
from apis.openstack_query_api.server_queries import find_server_with_flavors, group_by
from openstackquery import UserQuery
from tabulate import tabulate


def get_affected_flavors_html(flavor_list: List[str], eol_list: List[str]):
    table_html = "<table>"
    table_html += "<tr><th>Affected Flavors</th><th>EOL Date</th></tr>"
    for flavor, eol in zip(flavor_list, eol_list):
        table_html += f"<tr><td>{flavor}</td><td>{eol}</td></tr>"
    table_html += "</table>"
    return table_html


def get_affected_flavors_plaintext(flavor_list: List[str], eol_list: List[str]):
    rows = [
        {"Flavor": flavor, "EOL Date": eol}
        for flavor, eol in zip(flavor_list, eol_list)
    ]
    return tabulate(rows, headers="keys", tablefmt="plain")


def validate_flavor_input(
    flavor_name_list: List[str],
    flavor_eol_list: List[str],
    from_projects: List[str] = None,
    all_projects: bool = False,
):
    if not flavor_name_list:
        raise RuntimeError("please provide a list of flavor names to decommission")
    if not flavor_eol_list or len(flavor_name_list) != len(flavor_eol_list):
        raise RuntimeError("Each flavor must have a corresponding EOL date")
    for eol in flavor_eol_list:
        try:
            datetime.strptime(eol, "%Y/%m/%d")
        except ValueError as exc:
            raise RuntimeError("EOL date must be in format YYYY/MM/DD") from exc
    if from_projects and all_projects:
        raise RuntimeError(
            "given both project list and all_projects flag - please choose only one"
        )
    if not from_projects and not all_projects:
        raise RuntimeError(
            "please provide either a list of project identifiers or the 'all_projects' flag"
        )


def find_servers_with_decom_flavors(
    cloud_account: str,
    flavor_name_list: List[str],
    from_projects: Optional[List[str]] = None,
):
    server_query = find_server_with_flavors(
        cloud_account, flavor_name_list, from_projects
    )
    if not server_query.to_props():
        raise RuntimeError(
            f"No servers found with flavors {', '.join(flavor_name_list)} on projects "
            f"{','.join(from_projects) if from_projects else '[all projects]'}"
        )
    return group_by(server_query, "user_id")


def print_email_params(
    email_addr: str, user_name: str, as_html: bool, flavor_table: str, decom_table: str
):
    print(
        f"Send Email To: {email_addr}\n"
        f"email_templates decom-email: username {user_name}\n"
        f"send as html: {as_html}\n"
        f"flavor table: {flavor_table}\n"
        f"decom table: {decom_table}\n"
    )


def build_email_params(
    user_name: str, flavor_table: str, decom_table: str, **email_kwargs
):
    body = EmailTemplateDetails(
        template_name="decom_flavor",
        template_params={
            "username": user_name,
            "affected_flavors_table": flavor_table,
            "decom_table": decom_table,
        },
    )
    footer = EmailTemplateDetails(template_name="footer", template_params={})
    return EmailParams(email_templates=[body, footer], **email_kwargs)


def find_user_info(user_id, cloud_account, override_email_address):
    user_query = UserQuery()
    user_query.select("user_name", "user_email")
    user_query.where("equal_to", "user_id", value=user_id)
    user_query.run(cloud_account=cloud_account)
    res = user_query.to_props(flatten=True)
    if not res or not res["user_email"][0]:
        return "", override_email_address
    return res["user_name"][0], res["user_email"][0]


# pylint: disable=too-many-locals
def send_decom_flavor_email(
    smtp_account: SMTPAccount,
    cloud_account: Union[CloudDomains, str],
    flavor_name_list: List[str],
    flavor_eol_list: List[str],
    limit_by_projects: Optional[List[str]] = None,
    all_projects: bool = False,
    as_html: bool = False,
    send_email: bool = False,
    use_override: bool = False,
    override_email_address: Optional[str] = "cloud-support@stfc.ac.uk",
    cc_cloud_support: bool = False,
    **email_params_kwargs,
):
    validate_flavor_input(
        flavor_name_list, flavor_eol_list, limit_by_projects, all_projects
    )
    server_query = find_servers_with_decom_flavors(
        cloud_account, flavor_name_list, limit_by_projects
    )
    for user_id in server_query.to_props().keys():
        user_name, email_addr = find_user_info(
            user_id, cloud_account, override_email_address
        )
        send_to = [email_addr]
        if use_override:
            send_to = [override_email_address]
        if as_html:
            flavor_table = get_affected_flavors_html(flavor_name_list, flavor_eol_list)
        else:
            flavor_table = get_affected_flavors_plaintext(
                flavor_name_list, flavor_eol_list
            )
        if not send_email:
            print_email_params(
                send_to[0],
                user_name,
                as_html,
                flavor_table,
                server_query.to_string(groups=[user_id]),
            )
        else:
            email_params = build_email_params(
                user_name,
                flavor_table,
                (
                    server_query.to_string(groups=[user_id])
                    if not as_html
                    else server_query.to_html(groups=[user_id])
                ),
                email_to=send_to,
                as_html=as_html,
                email_cc=("cloud-support@stfc.ac.uk",) if cc_cloud_support else None,
                **email_params_kwargs,
            )
            Emailer(smtp_account).send_emails([email_params])
