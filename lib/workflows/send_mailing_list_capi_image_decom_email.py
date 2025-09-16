from datetime import datetime
from typing import Dict, List

from apis.email_api.emailer import Emailer
from apis.email_api.structs.email_params import EmailParams
from apis.email_api.structs.email_template_details import EmailTemplateDetails
from apis.email_api.structs.smtp_account import SMTPAccount
from tabulate import tabulate


def get_affected_images_html(image_info_list: List[Dict]):
    """
    returns information on images that are to be decommissioned as a html table
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
    returns information on images that are to be decommissioned as a plaintext tabulate table
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
    function validates key-word arguments related to displaying information on images to decommission and parses it
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


def print_email_params(email_addr: str, image_table: str):
    """
    Print email params instead of sending the email
    :param email_addr: email address to send to
    :param image_table: a table representing decommissioned images
    about VMs running with decommissioned images
    """

    print(f"Send Email To: {email_addr}\n" f"affected image table: {image_table}\n")


def build_email_params(image_table: str, **email_kwargs):
    """
    build email params dataclass which will be used to configure how to send the email
    :param image_table: a string table representing decommissioned images (names, EoL dates, upgraded images)
    :param email_kwargs: a set of email kwargs to pass to EmailParams
    """
    body = EmailTemplateDetails(
        template_name="mailing_list_capi_decom_image",
        template_params={"affected_images_table": image_table},
    )

    footer = EmailTemplateDetails(template_name="footer", template_params={})

    return EmailParams(email_templates=[body, footer], **email_kwargs)


def send_mailing_list_capi_image_decom_email(
    smtp_account: SMTPAccount,
    mailing_list: str,
    image_name_list: List[str],
    image_eol_list: List[str],
    image_upgrade_list: List[str],
    send_email: bool = False,
    as_html: bool = True,
    **email_params_kwargs,
):
    """
    Sends an email to the mailing list with a list of decommisioned CAPI images, and their replacements
    :param mailing_list: A string representing a mailing list email
    :param image_name_list: A list of image names to be decommissioned
    :param image_eol_list: A list of End of Life (EOL) date strings (YY/MM/DD) for images to be decommissioned
    :param image_upgrade_list: A list of image names that users are recommended to upgrade to
    :param send_email: Actually send the email instead of printing what will be sent
    :param email_params_kwargs: see EmailParams dataclass class docstring
    """

    image_data = get_image_info(image_name_list, image_eol_list, image_upgrade_list)

    if not send_email:
        print_email_params(mailing_list, image_table)
    else:
        if as_html:
            image_table = get_affected_images_html(image_data)
        else:
            image_table = get_affected_images_plaintext(image_data)

        email_params = build_email_params(
            image_table,
            email_to=mailing_list,
            as_html=as_html,
            **email_params_kwargs,
        )
        Emailer(smtp_account).send_emails([email_params])
