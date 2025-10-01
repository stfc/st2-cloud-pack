# pylint:disable=too-many-arguments
# pylint:disable=too-many-locals
from typing import List, Optional, Union

from apis.email_api.emailer import Emailer
from apis.email_api.structs.email_params import EmailParams
from apis.email_api.structs.email_template_details import EmailTemplateDetails
from apis.email_api.structs.smtp_account import SMTPAccount
from apis.openstack_api.enums.cloud_domains import CloudDomains
from tabulate import tabulate
from workflows.send_decom_flavor_email import (
    find_servers_with_decom_flavors,
    find_user_info,
)


def validate_input_arguments(
    flavor_name_list: List[str],
    from_projects: List[str] = None,
    all_projects: bool = False,
):
    """
    Validate input arguments for sending power testing emails.

    :param flavor_name_list: List of OpenStack flavor names that are under power testing review.
    :param planned_date_ranges: List of planned power testing dates associated with the flavors.
    :param from_projects: (Optional) List of project names or IDs to restrict the search scope.
    :param all_projects: If True, searches across all OpenStack projects.

    :raises RuntimeError: If required arguments are missing or if both `from_projects` and `all_projects` are set.
    """
    if not flavor_name_list:
        raise RuntimeError("please provide a list of flavor names to decommission")

    if from_projects and all_projects:
        raise RuntimeError(
            "given both project list and all_projects flag - please choose only one"
        )

    if not from_projects and not all_projects:
        raise RuntimeError(
            "please provide either a list of project identifiers or the 'all_projects' flag"
        )


def build_email_params(
    user_name: str,
    affected_flavors_table: str,
    affected_servers_table: str,
    **email_kwargs,
):
    """
    Construct EmailParams for notifying a user about flavors under power testing.

    :param user_name: Name of the OpenStack user receiving the email.
    :param affected_flavors_table: A rendered table (plain or HTML) listing affected flavors.
    :param affected_servers_table: A rendered table listing the user's VMs using affected flavors.
    :param email_kwargs: Additional keyword arguments for the EmailParams class.

    :return: EmailParams object containing templated email content and metadata.
    """
    body = EmailTemplateDetails(
        template_name="power_testing",
        template_params={
            "user_name": user_name,
            "affected_flavors_table": affected_flavors_table,
            "affected_servers_table": affected_servers_table,
        },
    )

    footer = EmailTemplateDetails(template_name="footer", template_params={})

    return EmailParams(email_templates=[body, footer], **email_kwargs)


def send_power_testing_email(
    smtp_account: SMTPAccount,
    cloud_account: Union[CloudDomains, str],
    flavor_name_list: List[str],
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
    Notify users by email if they own VMs using flavors scheduled for power testing.

    Each user receives a personalized email listing:
      - Flavors under review
      - Planned testing dates
      - Affected VMs they own

    :param smtp_account: SMTP configuration used to send the email.
    :param cloud_account: Name of the OpenStack account (from clouds.yaml) to authenticate with.
    :param flavor_name_list: List of flavor names that are under power testing or EOL consideration.
    :param limit_by_projects: (Optional) List of projects to scope the search to (mutually exclusive with all_projects).
    :param all_projects: If True, search all OpenStack projects for affected VMs.
    :param as_html: If True, emails are formatted as HTML; otherwise, plain text is used.
    :param send_email: If True, emails are actually sent; otherwise, the generated content is printed.
    :param use_override: If True, all emails are redirected to the override email address.
    :param override_email_address: Email address to use if override is enabled or if user's address is not found.
    :param cc_cloud_support: If True, cc cloud-support@stfc.ac.uk on all outgoing emails.
    :param email_params_kwargs: Additional arguments passed to EmailParams, such as subject or sender.
    """
    validate_input_arguments(flavor_name_list, limit_by_projects, all_projects)

    server_query = find_servers_with_decom_flavors(
        cloud_account, flavor_name_list, limit_by_projects
    )

    for user_id in server_query.to_props().keys():
        # if email_address not found - send to override_email_address
        # also send to override_email_address if override_email set
        user_name, email_addr = find_user_info(
            user_id, cloud_account, override_email_address
        )
        send_to = [email_addr]
        if use_override:
            send_to = [override_email_address]

        if as_html:
            affected_flavors_table = tabulate(
                [{"Flavor": flavor} for flavor in flavor_name_list],
                headers="keys",
                tablefmt="html",
            )
        else:
            affected_flavors_table = tabulate(
                [{"Flavor": flavor} for flavor in flavor_name_list],
                headers="keys",
                tablefmt="grid",
            )
        email_params = build_email_params(
            user_name=user_name,
            affected_flavors_table=affected_flavors_table,
            affected_servers_table=(
                server_query.to_string(groups=[user_id])
                if not as_html
                else server_query.to_html(groups=[user_id])
            ),
            email_to=send_to,
            as_html=as_html,
            email_cc=("cloud-support@stfc.ac.uk",) if cc_cloud_support else None,
            **email_params_kwargs,
        )

        if not send_email:
            Emailer(smtp_account).print_email(email_params)

        else:
            Emailer(smtp_account).send_emails([email_params])
