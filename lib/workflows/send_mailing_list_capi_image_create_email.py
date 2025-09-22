from typing import Dict, List

from apis.email_api.emailer import Emailer
from apis.email_api.structs.email_params import EmailParams
from apis.email_api.structs.email_template_details import EmailTemplateDetails
from apis.email_api.structs.smtp_account import SMTPAccount
from tabulate import tabulate


def get_created_images_html(image_info_list: List[Dict]):
    """
    returns information on images that have been created as a html table
    :param image_info_list: A list of dictionaries containing information on images that have been created
    """

    table_html = "<table>"
    table_html += "<tr><th>Created Images</th></tr>"
    for image in image_info_list:
        table_html += f"<tr><td>{image['name']}</td></tr>"
    table_html += "</table>"
    return table_html


def get_created_images_plaintext(image_info_list: List[Dict]):
    """
    returns information on images that have been created as a plaintext tabulate table
    :param image_info_list: A list of dictionaries containing information on images that have been created
    """
    return tabulate(
        image_info_list,
        headers={"name": "Created Images"},
        tablefmt="plain",
    )


def get_image_info(image_name_list: List[str]):
    """
    function validates key-word arguments related to displaying information on images that have been
    created and parses it into a list of dictionaries
    """
    if len(image_name_list) == 0:
        raise RuntimeError(
            "please provide a list of image names that have been created"
        )

    img_list = []
    for image_name in image_name_list:
        img_list.append({"name": image_name})

    return img_list


def print_email_params(email_addr: str, image_table: str):
    """
    Print email params instead of sending the email
    :param email_addr: email address to send to
    :param image_table: a table representing created images
    """

    print(f"Send Email To: {email_addr}\n" f"Created image table: {image_table}\n")


def build_email_params(image_table: str, **email_kwargs):
    """
    build email params dataclass which will be used to configure how to send the email
    :param image_table: a string table representing created images
    :param email_kwargs: a set of email kwargs to pass to EmailParams
    """
    body = EmailTemplateDetails(
        template_name="mailing_list_capi_create_image",
        template_params={"created_images_table": image_table},
    )

    footer = EmailTemplateDetails(template_name="footer", template_params={})

    return EmailParams(email_templates=[body, footer], **email_kwargs)


def send_mailing_list_capi_image_create_email(
    smtp_account: SMTPAccount,
    mailing_list: str,
    image_name_list: List[str],
    send_email: bool = False,
    as_html: bool = True,
    **email_params_kwargs,
):
    """
    Sends an email to the mailing list with a list of created CAPI images.
    :param mailing_list: A string representing a mailing list email
    :param image_name_list: A list of image names that have been created
    :param send_email: Actually send the email instead of printing what will be sent
    :param email_params_kwargs: see EmailParams dataclass class docstring
    """

    image_data = get_image_info(image_name_list)

    if as_html:
        image_table = get_created_images_html(image_data)
    else:
        image_table = get_created_images_plaintext(image_data)

    if not send_email:
        print_email_params(mailing_list, image_table)
    else:
        email_params = build_email_params(
            image_table,
            email_to=[mailing_list],
            as_html=as_html,
            **email_params_kwargs,
        )
        Emailer(smtp_account).send_emails([email_params])
