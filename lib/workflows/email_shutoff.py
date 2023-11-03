from typing import List, Optional, Dict, Tuple
from openstack_query.api.query_objects import ServerQuery
from enums.query.props.server_properties import ServerProperties
from enums.query.props.user_properties import UserProperties
from structs.email.email_params import EmailParams
from enums.query.query_presets import QueryPresetsGeneric
from email_api.emailer import Emailer
from structs.email.smtp_account import SMTPAccount


def query_shutoff_vms(project_id: Optional[List[str]] = None):
    """
    Sends an email to a user about a shutoff (stopped) VM
    :param project_id: optional field to provide a list of project IDs for specific projects,
    otherwise query all projects
    :returns: Dictionary with a list of VM names grouped by user ID
    """

    query_obj = ServerQuery()

    query_obj.select(
        ServerProperties.SERVER_NAME
    ).where(
        QueryPresetsGeneric.EQUAL_TO,
        ServerProperties.SERVER_STATUS,
        value="SHUTOFF")

    # if project ID provided as parameter
    if project_id:
        query_obj.run(
            "openstack",
            as_admin=True,
            from_projects=project_id
        )

    else:
        query_obj.run(
            "openstack",
            as_admin=True,
            all_projects=True
        )

    user_query = query_obj.then("USER_QUERY", keep_previous_results=True)

    user_query.select(
        UserProperties.USER_EMAIL
    ).group_by(
        UserProperties.USER_NAME
    )

    if project_id:
        user_query.run(
            "openstack",
            # from_projects=project_id
        )

    else:
        user_query.run("openstack", as_admin=True, all_projects=True)

    res = user_query.to_props()

    return res


def prepare_user_server_email(server_query_result: List[Dict]) -> Tuple[str, List[str]]:
    """
    Extracts the user email and list of server names from a
    query object
    :param: server_query_object: A list of dictionaries containing results from a query
    :returns: A tuple containing the user email and list of VM names
    """
    details = server_query_result
    # store user email
    assert all(details[0]['user_email'] == i['user_email'] for i in details)
    user_email = details[0]['user_email']
    # extract list of server names
    server_names = [d['server_name'] for d in server_query_result]
    return user_email, server_names


def send_user_email(smtp_account: SMTPAccount, user_email: str, subject_text: str, email_templates=None):
    """
    Sends an email to a user
    :param: smtp_account: SMTP account object with Emailer config
    :param: user_email: Email address for a specific user
    :param: subject_text: Subject for the email
    """

    if not user_email:
        user_email = "cloud-support@stfc.ac.uk"

    test_params = EmailParams(
        subject=subject_text,
        email_from='cloud-support@stfc.ac.uk',
        email_to=[user_email],
        email_templates=[]
    )

    Emailer(smtp_account).send_emails([test_params])


def main(smtp_account: SMTPAccount, project_id: Optional[List[str]] = None):
    """
    The main method for running the workflow.
    :param: project_id: (Optional) A list of project IDs to query from
    """

    # get VMs shutoff, grouped by user, include user email in results
    shutoff_vm = query_shutoff_vms(project_id)

    for user in shutoff_vm.values():
        user_email, server_name_list = prepare_user_server_email(user) # shutoff_vm[user] is list of dictionaries
        send_user_email(smtp_account, user_email, server_name_list)

