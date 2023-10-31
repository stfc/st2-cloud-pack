from enums.cloud_domains import CloudDomains
from openstack_query.api.query_objects import ServerQuery
from openstack_query.api.query_objects import UserQuery
from enums.query.props.server_properties import ServerProperties
from enums.query.props.user_properties import UserProperties
from structs.email.email_params import EmailParams
from enums.query.query_presets import QueryPresetsGeneric
from email_api.emailer import Emailer
from tabulate import tabulate

from structs.email.smtp_account import SMTPAccount


def query_shutoff_vms(project_id=None):
    """
    Sends an email to a user about a shutoff (stopped) VM
    :param project_id: optional field to provide the ID for a specific project
    :returns: Dictionary with a list of VM names grouped by user ID
    """

    query_obj = ServerQuery()

    query_obj.select(
        ServerProperties.SERVER_NAME
    ).where(
        QueryPresetsGeneric.EQUAL_TO,
        ServerProperties.SERVER_STATUS,
        value="STOPPED"
    ).group_by(
        ServerProperties.USER_ID
    )

    # if project ID provided as parameter
    if project_id:
        query_obj.run(
            "openstack",
            from_projects=project_id
        )

    else:
        query_obj.run(
            "openstack"
        )

    query_result = query_obj.to_list()

    return query_result


def query_user_details(user_id):
    """
    Queries OpenStack for the username and user email using
    a user ID
    :param user_id: ID for a given user
    :returns: List of dictionaries with matching username and email
    """
    query_obj = UserQuery()

    query_obj.select(
        UserProperties.USER_NAME,
        UserProperties.USER_EMAIL
    ).where(
        QueryPresetsGeneric.EQUAL_TO,
        UserProperties.USER_ID,
        value=user_id
    )

    query_obj.run(
        "openstack"
    )

    query_result = query_obj.to_list()

    return query_result


def extract_user_details(user_list):
    """
    Using a list of user IDs, this method queries for the name and email
    address that match each user ID
    :param user_list: A list of user IDs
    :returns: A tuple of dictionaries containing the username and emails respectively matching the user IDs

    """
    user_names = dict()
    user_emails = dict()
    for user in user_list:
        # get username and details
        user_detail = query_user_details(user)
        user_detail = user_detail[0]

        user_names[user] = user_detail['user_name']
        user_emails[user] = user_detail['user_email']

        if not user_emails[user]:
            raise KeyError(
                f"Missing user email for {user} {user_detail['user_name']}"
            )


    return user_names, user_emails

def send_user_email(user_email, subject_text, email_templates=None):
    """
    Sends an email to a user
    :param: user_email: Email address for a specific user
    :param: subject_text: Subject for the email
    """

    email_account = SMTPAccount.from_dict({"account_details"})
    test_params = EmailParams(
        subject=subject_text,
        email_from='support@example.com',
        email_to=user_email,
        email_templates=[]
    )

    Emailer(email_account).send_emails([test_params])


def main():
    # script for testing within own scratch space project

    project_id = ['project_id']


    user_email_test = ["user@example.com"]  # initially hardcoded for now

    # get all VMs in shutoff state in a specific project, group by user ID
    instance_list = query_shutoff_vms(project_id)

    # from VM query, get all user IDs
    user_list = instance_list.keys()

    extract_user_details(instance_list, user_email_test, user_list)

    # for vm in user_vms:
    #     vm_name = vm["server_name"]
    #     message = f'Test email - VM in shutoff state: {vm_name}'
    #     print(message)
    # print(f'Email message subject preview before sending: {message}')
    # send_email(user_email_test, message)
    # break






#        print(f'Results for user: {user_name} Email: {user_email}')

#        user_vms = (instance_list[user])



if __name__ == "__main__":
    main()
