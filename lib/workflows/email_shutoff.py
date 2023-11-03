from typing import List, Optional, Dict, Tuple
from openstack_query.api.query_objects import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enums.query.props.user_properties import UserProperties
from structs.email.email_params import EmailParams
from enums.query.query_presets import QueryPresetsGeneric, QueryPresetsDateTime
from email_api.emailer import Emailer
from structs.email.smtp_account import SMTPAccount


def query_shutoff_vms(
    cloud_account: str,
    project_id: Optional[List[str]] = None,
    days_threshold: int = None,
):
    """
    Sends an email to a user about a shutoff (stopped) VM
    :param cloud_account: Cloud account to use for running query
    :param project_id: optional field to provide a list of project IDs for specific projects,
    otherwise query all projects
    :param days_threshold: param to query servers updated to be in shutoff state the last 30 days by default
    :returns: Dictionary with a list of VM names grouped by user ID
    """

    query_obj = ServerQuery()

    query_obj.select(ServerProperties.SERVER_NAME).where(
        QueryPresetsGeneric.EQUAL_TO, ServerProperties.SERVER_STATUS, value="SHUTOFF"
    ).where(
        QueryPresetsDateTime.OLDER_THAN,
        ServerProperties.SERVER_LAST_UPDATED_DATE,
        days=days_threshold,
    )

    # if project ID provided as parameter
    if project_id:
        query_obj.run(cloud_account, as_admin=True, from_projects=project_id)

    else:
        query_obj.run(cloud_account, as_admin=True, all_projects=True)

    user_query = query_obj.then("USER_QUERY", keep_previous_results=True)

    user_query.select(UserProperties.USER_EMAIL).group_by(UserProperties.USER_NAME)

    user_query.run(cloud_account)

    res = user_query.to_props()

    return res


def prepare_user_server_email(server_query_result: List[Dict]) -> Tuple[str, List[str]]:
    """
    Extracts the user email and list of server names from a
    query object
    :param server_query_result: A list of dictionaries containing results from a query
    :returns: A tuple containing the user email and list of VM names
    """
    details = server_query_result
    # store user email
    assert all(details[0]["user_email"] == i["user_email"] for i in details)
    user_email = details[0]["user_email"]
    # extract list of server names
    server_names = [d["server_name"] for d in server_query_result]
    return user_email, server_names


def send_user_email(
    smtp_account: SMTPAccount,
    email_from: str,
    user_email: str,
    server_list: List[str],
    email_templates=None,
):
    """
    Sends an email to a user
    :param smtp_account: SMTP account object with Emailer config
    :param email_from: Email address to email from
    :param user_email: Email address for a specific user
    :param server_list: List of servers from a query
    :param email_templates: Template to use for emails
    """
    # For now, subject is the list of VMs in shutoff state

    if not user_email:
        user_email = "cloud-support@stfc.ac.uk"

    subject = f"VM Shutoff {server_list}"
    email_params = EmailParams(
        subject=subject,
        email_from=email_from,
        email_to=[user_email],
        email_templates=[],
    )

    Emailer(smtp_account).send_emails([email_params])


def main(
    smtp_account: SMTPAccount,
    cloud_account: str = "openstack",
    email_from: str = "cloud-support@stfc.ac.uk",
    limit_by_project: Optional[List[str]] = None,
    days_threshold: int = 30,
):
    """
    The main method for running the workflow
    :param smtp_account: SMTPAccount object to use for emailing
    :param cloud_account: Name of cloud account to use e.g. "openstack"
    :param email_from: Email to send from
    :param limit_by_project: (Optional) A list of project IDs to query from
    :param days_threshold: Check for VMs updated in last 30 days in SHUTOFF state
    """

    # get VMs shutoff, grouped by user, include user email in results
    shutoff_vm = query_shutoff_vms(cloud_account, limit_by_project, days_threshold)

    for user in shutoff_vm.values():
        user_email, server_name_list = prepare_user_server_email(
            user
        )  # shutoff_vm[user] is list of dictionaries

        send_user_email(smtp_account, email_from, user_email, server_name_list)
