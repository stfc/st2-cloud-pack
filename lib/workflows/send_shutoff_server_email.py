import dataclasses
from typing import List, Optional, Dict

from email_api.emailer import Emailer
from enums.query.props.server_properties import ServerProperties
from enums.query.props.user_properties import UserProperties
from enums.query.query_presets import QueryPresetsGeneric, QueryPresetsDateTime
from openstack_query.api.query_objects import ServerQuery, UserQuery
from structs.email.email_params import EmailParams
from structs.email.smtp_account import SMTPAccount


@dataclasses.dataclass
class UserDetails:
    """
    Dataclass for user details
    """

    id: str
    name: str
    email: str


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


def find_user_info(
    user_id: str, cloud_account: str, use_override: bool, override_email: Optional[str]
) -> UserDetails:
    """
    Run UserQuery to find user name and user email associated with a VM
    :param user_id: openstack user id
    :param cloud_account: openstack account to use to run the query
    :param override_email_address: email address if user does not have an email address
    :returns: Tuple containing user name and user email
    """

    user_query = UserQuery()
    user_query.select(UserProperties.USER_NAME, UserProperties.USER_EMAIL).where(
        QueryPresetsGeneric.EQUAL_TO, UserProperties.USER_ID, value=user_id
    )

    user_query.run(cloud_account=cloud_account)

    res = user_query.to_props(flatten=True)

    if not res:
        return UserDetails(user_id, "", override_email if use_override else None)

    return UserDetails(user_id, res["user_name"][0], res["user_email"][0])


def extract_server_list(server_query_result: List[Dict]) -> List[str]:
    """
    Extracts the list of server names from a query object
    :param server_query_result: A list of dictionaries containing results from a query
    :returns: A tuple containing the user email and list of VM names
    """

    # extract list of server names
    server_names = [d["server_name"] for d in server_query_result]
    return server_names


# pylint: disable=too-many-arguments
def send_user_email(
    smtp_account: SMTPAccount,
    email_from: str,
    user_email: str,
    cc_cloud_support: bool,
    server_list: List[str],
    email_templates,
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
        email_cc=("cloud-support@stfc.ac.uk",) if cc_cloud_support else None,
        email_templates=[email_templates],
    )

    Emailer(smtp_account).send_emails([email_params])


# pylint: disable=too-many-arguments
def send_shutoff_server_email(
    smtp_account: SMTPAccount,
    cloud_account: str = "openstack",
    email_from: str = "cloud-support@stfc.ac.uk",
    use_override: bool = True,
    override_email_address: Optional[str] = "cloud-support@stfc.ac.uk",
    limit_by_project: Optional[List[str]] = None,
    days_threshold: int = 30,
    email_template="test",
    cc_cloud_support: bool = False,
    send_email: bool = False,
):
    """
    The main method for running the workflow
    :param smtp_account: SMTPAccount object to use for emailing
    :param cloud_account: Name of cloud account to use e.g. "openstack"
    :param email_from: Email to send from
    :param override_email_address: Default address for a user if query not valid
    :param limit_by_project: (Optional) A list of project IDs to query from
    :param days_threshold: Check for VMs updated in last 30 days in SHUTOFF state
    """

    # get VMs shutoff, grouped by user, include user email in results
    shutoff_vm = query_shutoff_vms(cloud_account, limit_by_project, days_threshold)

    for user in shutoff_vm.values():
        # extract username and user email
        user_details = find_user_info(
            user, cloud_account, use_override, override_email_address
        )
        # extract list of VM names
        server_name_list = extract_server_list(user)
        # send email
        if send_email:
            send_user_email(
                smtp_account,
                email_from,
                user_details.email,
                cc_cloud_support,
                server_name_list,
                email_template,
            )
        else:
            print("query complete")
