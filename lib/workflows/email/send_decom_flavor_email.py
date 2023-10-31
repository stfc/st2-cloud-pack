from typing import List, Optional, Union

from openstack_query import FlavorQuery

from enums.query.sort_order import SortOrder
from enums.cloud_domains import CloudDomains
from enums.query.query_presets import QueryPresetsGeneric
from enums.query.props.flavor_properties import FlavorProperties
from enums.query.props.server_properties import ServerProperties
from enums.query.props.project_properties import ProjectProperties
from enums.query.props.user_properties import UserProperties

from structs.email.smtp_account import SMTPAccount
from structs.email.email_template_details import EmailTemplateDetails
from structs.email.email_params import EmailParams

from email_api.emailer import Emailer


def validate(
    flavor_name_list: List[str],
    from_projects: List[str] = None,
    all_projects: bool = False,
):
    """
    Validate incoming kwargs to ensure they are valid
    :param flavor_name_list: list of flavor names to limit query by
    :param from_projects: list of projects to limit query by
    :param all_projects: a flag which if set, will run the query on all projects
    """
    if not flavor_name_list:
        raise RuntimeError("please provide a list of flavor names to decommission")

    if from_projects and all_projects:
        raise RuntimeError(
            "given both project list and all_projects flag - please choose only one"
        )

    if not from_projects and not all_projects:
        raise RuntimeError(
            "please provide either a list of project identifiers or with flag 'all_projects' to run globally"
        )


def find_users_with_decom_flavors(
    cloud_account: str,
    flavor_name_list: List[str],
    from_projects: Optional[List[str]] = None,
):
    """
    Use QueryAPI to run the query to find decom flavors
    :param cloud_account: string represents cloud account to use
    :param flavor_name_list: A list of flavor names to be decommissioned
    :param from_projects: A list of project identifiers to limit search in
    """

    flavor_query = (
        FlavorQuery()
        .where(
            QueryPresetsGeneric.EQUAL_TO, FlavorProperties.FLAVOR_IS_PUBLIC, value=True
        )
        .where(
            QueryPresetsGeneric.ANY_IN,
            FlavorProperties.FLAVOR_NAME,
            values=flavor_name_list,
        )
        .run(cloud_account)
        .sort_by((FlavorProperties.FLAVOR_ID, SortOrder.ASC))
    )

    # find the VMs using flavors we found from the flavor query
    server_query = (
        flavor_query.then("SERVER_QUERY", keep_previous_results=True)
        .run(
            cloud_account,
            as_admin=True,
            from_projects=from_projects if from_projects else None,
            all_projects=not from_projects,
        )
        .append_from("PROJECT_QUERY", cloud_account, ProjectProperties.PROJECT_NAME)
        .select(
            ServerProperties.SERVER_ID,
            ServerProperties.SERVER_NAME,
            ServerProperties.ADDRESSES,
        )
    )

    # find the users who own the VMs we found from the server query
    user_query = (
        server_query.then("USER_QUERY", keep_previous_results=True)
        .run(cloud_account)
        .select(UserProperties.USER_NAME)
        .group_by(UserProperties.USER_EMAIL)
    )

    return user_query


def print_email_params(
    email_addr: str, user_name: str, as_html: bool, flavor_table: str, decom_table: str
):
    """
    Print email params instead of sending the email
    :param email_addr: email address to send to
    :param user_name: name of user in openstack
    :param as_html: A boolean which if selected will send an email, otherwise prints email details only
    :param flavor_table: a table representing decommissioned flavors
    :param decom_table: a table representing info found in openstack
    about VMs running with decommissioned flavors
    """
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
    """
    build email params dataclass which will be used to configure how to send the email
    :param user_name: name of user in openstack
    :param flavor_table: a table representing decommissioned flavors
    :param decom_table: a table representing info found in openstack about VMs
        running with decommissioned flavors
    :param email_kwargs: a set of email kwargs to pass to EmailParams
    """
    body = EmailTemplateDetails(
        template_name="decom_email",
        template_params={
            "username": user_name,
            "affected_flavors_table": flavor_table,
            "decom_table": decom_table,
        },
    )

    footer = EmailTemplateDetails(template_name="footer", template_params={})

    return EmailParams(email_templates=[body, footer], **email_kwargs)


# pylint:disable=too-many-arguments
# pylint:disable=too-many-locals
def send_decom_flavor_email(
    smtp_account: SMTPAccount,
    cloud_account: Union[CloudDomains, str],
    flavor_name_list: List[str],
    from_projects: Optional[List[str]] = None,
    all_projects: bool = False,
    as_html: bool = False,
    send_email: bool = False,
    override_email: bool = False,
    override_email_address: str = "cloud-support@stfc.ac.uk",
    **email_params_kwargs,
):
    """
    Sends an email to each user who owns one or more VMs that have a flavor that is to be decommissioned.
    This email will contain a notice to delete or rebuild the VM
    :param smtp_account: (SMTPAccount): SMTP config
    :param cloud_account: string represents cloud account to use
    :param flavor_name_list: A list of flavor names to be decommissioned
    :param from_projects: A list of projects to limit search in
    :param all_projects: A boolean which if selected will search in all projects
    :param send_email: Actually send the email instead of printing what will be sent
    :param as_html: Send email as html
    :param override_email: an overriding email to send the email to if override flag set
    :param override_email_address: an overriding email address to use if override_email set
    :param email_params_kwargs: see EmailParams dataclass class docstring
    """

    validate(flavor_name_list, from_projects, all_projects)
    user_query = find_users_with_decom_flavors(
        cloud_account, flavor_name_list, from_projects
    )

    for email_addr, outputs in user_query.to_props().items():
        user_name = outputs[0]["user_name"]

        # if email_address not found - send to override_email_address
        # also send to override_email_address if override_email set

        send_to = email_addr
        if override_email or not email_addr:
            send_to = override_email_address

        if not send_email:
            print_email_params(
                send_to,
                user_name,
                as_html,
                ", ".join(flavor_name_list),
                user_query.to_string(groups=[email_addr]),
            )

        else:
            email_params = build_email_params(
                user_name,
                ", ".join(flavor_name_list),
                user_query.to_string(groups=[email_addr]),
                email_to=email_addr if not override_email else override_email_address,
                as_html=as_html,
                **email_params_kwargs,
            )
            Emailer(smtp_account).send_emails(email_params)
