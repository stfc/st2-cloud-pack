from datetime import datetime
from typing import Dict, List, Optional, Union

from apis.email_api.emailer import Emailer
from apis.email_api.structs.email_params import EmailParams
from apis.email_api.structs.email_template_details import EmailTemplateDetails
from apis.email_api.structs.smtp_account import SMTPAccount
from apis.openstack_api.enums.cloud_domains import CloudDomains
from apis.openstack_query_api.server_queries import (
    find_servers_with_image,
    group_servers_by_user_id,
)
from apis.openstack_query_api.user_queries import find_user_info
from tabulate import tabulate


def get_affected_images_html(image_info_list: List[Dict]):
    """
    Returns information on images that are to be decommissioned as a html table.
    :param image_info_list: A list of dictionaries containing information on images that are to be decommissioned
    """
    table_html = "<table>"
    table_html += "<tr><th>Affected Images</th><th>EOL Date</th><th>Recommended Upgraded Image</th></tr>"
    for image in image_info_list:
        table_html += f"<tr><td>{image['name']}</td><td>{image['eol']}</td><td>{image['upgrade']}</td></tr>"
    table_html += "</table>"
    return table_html


def get_affected_images_plaintext(image_info_list: List[Dict]):
    """
    Returns information on images that are to be decommissioned as a plaintext tabulate table
    :param image_info_list: A list of dictionaries containing information on images that are to be decommissioned
    """
    return tabulate(
        image_info_list,
        headers={
            "name": "Affected Images",
            "eol": "EOL Date",
            "upgrade": "Recommended Upgrade Image",
        },
        tablefmt="plain",
    )


def get_image_info(
    image_name_list: List[str],
    image_eol_list: List[str],
    image_upgrade_list: List[str],
):
    """
    Function validates key-word arguments related to displaying information on images to decommission and parses it
    into a list of dictionaries
    """
    if len(image_name_list) == 0:
        raise RuntimeError("please provide a list of image names to decommission")

    if not len(image_name_list) == len(image_eol_list):
        raise RuntimeError(
            "Lists un-equal: Each image to decommission requires an EOL date"
        )

    if not len(image_name_list) == len(image_upgrade_list):
        raise RuntimeError(
            "Lists un-equal: Each image to decommission requires a recommended upgraded image to replace it, "
            "leave empty string '' per image to specify if no upgrade image exists (and deletion is recommended)"
        )

    img_list = []
    for image_name, eol, upgrade_image in zip(
        image_name_list, image_eol_list, image_upgrade_list
    ):
        try:
            datetime.strptime(eol, "%Y/%m/%d")
        except ValueError as exp:
            raise RuntimeError(
                "End Of Life string must be in format YYYY/MM/DD"
            ) from exp
        if upgrade_image.lower() in ("", "none"):
            upgrade_image = "None (deletion recommended)"
        img_list.append({"name": image_name, "eol": eol, "upgrade": upgrade_image})
    return img_list


def print_email_params(
    email_addr: str,
    user_name: str,
    as_html: bool,
    image_table: str,
    decom_table: str,
):
    """
    Print email params instead of sending the email
    :param email_addr: Email address to send to
    :param user_name: Name of user in OpenStack
    :param as_html: A boolean which, if selected, will send an email - otherwise, prints email details only
    :param image_table: A table representing decommissioned images
    :param decom_table: A table representing info found in OpenStack about VMs running with decommissioned images
    """
    print(
        f"Send Email To: {email_addr}\n"
        f"email_templates decom-email: username {user_name}\n"
        f"send as html: {as_html}\n"
        f"affected image table: {image_table}\n"
        f"decom table: {decom_table}\n"
    )


def build_email_params(
    user_name: str,
    image_table: str,
    decom_table: str,
    **email_kwargs,
):
    """
    Builds email params dataclass which will be used to configure how to send the email
    :param user_name: Name of user in OpenStack
    :param image_table: A table representing decommissioned images
    :param decom_table: A table representing info found in OpenStack about VMs running with decommissioned images
    :param email_kwargs: A set of email kwargs to pass to EmailParams
    """
    body = EmailTemplateDetails(
        template_name="decom_image",
        template_params={
            "username": user_name,
            "affected_images_table": image_table,
            "decom_table": decom_table,
        },
    )

    footer = EmailTemplateDetails(template_name="footer", template_params={})

    return EmailParams(email_templates=[body, footer], **email_kwargs)


# pylint:disable=too-many-arguments
# pylint:disable=too-many-locals
def send_decom_image_email(
    smtp_account: SMTPAccount,
    cloud_account: Union[CloudDomains, str],
    image_name_list: List[str],
    image_eol_list: List[str],
    image_upgrade_list: List[str],
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
    Sends an email to each user who owns one or more VMs that are running an image that is to be decommissioned.
    This email will contain a notice to delete or rebuild the VM.
    :param smtp_account: (SMTPAccount): SMTP config
    :param cloud_account: String representing the cloud account to use
    :param image_name_list: A list of image names to be decommissioned
    :param image_eol_list: A list of End of Life (EOL) date strings (YY/MM/DD) for images to be decommissioned
    :param image_upgrade_list: A list of image names that users are recommended to upgrade to
    :param limit_by_projects: A list of project names or ids to limit search in
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

    decom_image_info = get_image_info(
        image_name_list, image_eol_list, image_upgrade_list
    )
    server_query = find_servers_with_image(
        cloud_account, image_name_list, limit_by_projects
    )

    if not server_query.to_props():
        raise RuntimeError(
            f"No servers found with images {', '.join(image_name_list)} on projects "
            f"{','.join(limit_by_projects) if limit_by_projects else '[all projects]'}"
        )

    grouped_query = group_servers_by_user_id(server_query)

    for user_id in grouped_query.to_props().keys():
        # if email_address not found - send to override_email_address
        # also send to override_email_address if override_email set
        user_name, email_addr = find_user_info(
            user_id, cloud_account, override_email_address
        )
        send_to = [email_addr]
        if use_override:
            send_to = [override_email_address]

        if not send_email:
            print_email_params(
                send_to[0],
                user_name,
                as_html,
                get_affected_images_plaintext(decom_image_info),
                grouped_query.to_string(groups=[user_id], include_group_titles=False),
            )

        else:
            if as_html:
                image_list = get_affected_images_html(decom_image_info)
                server_list = grouped_query.to_html(
                    groups=[user_id], include_group_titles=False
                )
            else:
                image_list = get_affected_images_plaintext(decom_image_info)
                server_list = grouped_query.to_string(
                    groups=[user_id], include_group_titles=False
                )

            email_params = build_email_params(
                user_name,
                image_list,
                server_list,
                email_to=send_to,
                as_html=as_html,
                email_cc=("cloud-support@stfc.ac.uk",) if cc_cloud_support else None,
                **email_params_kwargs,
            )
            Emailer(smtp_account).send_emails([email_params])
