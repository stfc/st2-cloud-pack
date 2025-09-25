from unittest.mock import NonCallableMock, call, patch

import pytest
from workflows.send_mailing_list_capi_image_create_email import (
    build_email_params,
    get_created_images_html,
    get_created_images_plaintext,
    get_image_info,
    print_email_params,
    send_mailing_list_capi_image_create_email,
)


def test_get_created_images_html():
    """
    Tests that get_created_images_html returns a html formatted list given valid inputs
    """
    res = get_created_images_html(
        [
            {"name": "img1"},
            {"name": "img2"},
        ]
    )
    assert res == (
        "<table>"
        "<tr><th>Created Images</th></tr>"
        "<tr><td>img1</td></tr>"
        "<tr><td>img2</td></tr>"
        "</table>"
    )


@patch("workflows.send_mailing_list_capi_image_create_email.tabulate")
def test_get_created_images_plaintext(mock_tabulate):
    """
    Tests that get_created_plaintext calls tabulate correctly
    """
    mock_image_info = [
        {"name": "img1"},
        {"name": "img2"},
    ]
    res = get_created_images_plaintext(mock_image_info)
    mock_tabulate.assert_called_once_with(
        mock_image_info,
        headers={"name": "Created Images"},
        tablefmt="plain",
    )
    assert res == mock_tabulate.return_value


def test_get_image_info_image_list_empty():
    """Tests that get_image_info returns error when passed empty image name list"""
    with pytest.raises(RuntimeError):
        get_image_info([])


def test_get_image_info_valid():
    """Tests that get_image_info returns parsed list of dicts when inputs are valid"""
    res = get_image_info(["img1", "img2"])
    print()
    assert res == [{"name": "img1"}, {"name": "img2"}]


def test_print_email_params():
    """
    Test print_email_params() function simply prints values
    """
    email_addr = "test@example.com"
    image_table = "Image Table Content"

    with patch("builtins.print") as mock_print:
        print_email_params(email_addr, image_table)

    mock_print.assert_called_once_with(
        f"Send Email To: {email_addr}\n" f"Created image table: {image_table}\n"
    )


@patch("workflows.send_mailing_list_capi_image_create_email.EmailTemplateDetails")
@patch("workflows.send_mailing_list_capi_image_create_email.EmailParams")
def test_build_params(mock_email_params, mock_email_template_details):
    """
    Test build_params() function creates email params appropriately and returns them
    """

    image_table = "Image Table Content"
    email_kwargs = {"arg1": "val1", "arg2": "val2"}

    res = build_email_params(image_table, **email_kwargs)
    mock_email_template_details.assert_has_calls(
        [
            call(
                template_name="mailing_list_capi_create_image",
                template_params={
                    "created_images_table": image_table,
                },
            ),
            call(template_name="footer", template_params={}),
        ]
    )

    mock_email_params.assert_called_once_with(
        email_templates=[
            mock_email_template_details.return_value,
            mock_email_template_details.return_value,
        ],
        arg1="val1",
        arg2="val2",
    )

    assert res == mock_email_params.return_value


@patch("workflows.send_mailing_list_capi_image_create_email.get_image_info")
@patch(
    "workflows.send_mailing_list_capi_image_create_email.get_created_images_plaintext"
)
@patch("workflows.send_mailing_list_capi_image_create_email.build_email_params")
@patch("workflows.send_mailing_list_capi_image_create_email.Emailer")
def test_send_mailing_list_capi_image_create_email_send_plaintext(
    mock_emailer,
    mock_build_email_params,
    mock_get_created_images_plaintext,
    mock_get_image_info,
):
    """
    Tests send_mailing_list_capi_image_create_email() function actually sends email - as_html False
    """
    image_name_list = ["img1", "img2"]
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    send_mailing_list_capi_image_create_email(
        smtp_account=smtp_account,
        mailing_list="mailing list email",
        image_name_list=image_name_list,
        as_html=False,
        send_email=True,
        **mock_kwargs,
    )

    mock_get_image_info.assert_called_once_with(image_name_list)

    mock_build_email_params.assert_called_once_with(
        mock_get_created_images_plaintext.return_value,
        email_to=["mailing list email"],
        as_html=False,
        **mock_kwargs,
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )


@patch("workflows.send_mailing_list_capi_image_create_email.get_image_info")
@patch("workflows.send_mailing_list_capi_image_create_email.get_created_images_html")
@patch("workflows.send_mailing_list_capi_image_create_email.build_email_params")
@patch("workflows.send_mailing_list_capi_image_create_email.Emailer")
def test_send_mailing_list_capi_image_create_email_send_html(
    mock_emailer,
    mock_build_email_params,
    mock_get_created_images_html,
    mock_get_image_info,
):
    """
    Tests send_mailing_list_capi_image_create_email() function actually sends email - as_html True
    """
    image_name_list = ["img1", "img2"]
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    send_mailing_list_capi_image_create_email(
        smtp_account=smtp_account,
        mailing_list="mailing list email",
        image_name_list=image_name_list,
        as_html=True,
        send_email=True,
        **mock_kwargs,
    )

    mock_get_image_info.assert_called_once_with(image_name_list)

    mock_build_email_params.assert_called_once_with(
        mock_get_created_images_html.return_value,
        email_to=["mailing list email"],
        as_html=True,
        **mock_kwargs,
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )


@patch("workflows.send_mailing_list_capi_image_create_email.get_image_info")
@patch(
    "workflows.send_mailing_list_capi_image_create_email.get_created_images_plaintext"
)
@patch("workflows.send_mailing_list_capi_image_create_email.print_email_params")
def test_send_mailing_list_capi_image_create_email_print_email(
    mock_print_email_params,
    mock_get_created_images_plaintext,
    mock_get_image_info,
):
    """
    Tests send_mailing_list_capi_image_create_email() function actually sends email - as_html false
    """
    image_name_list = ["img1", "img2"]
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    send_mailing_list_capi_image_create_email(
        smtp_account=smtp_account,
        mailing_list="mailing list email",
        image_name_list=image_name_list,
        as_html=False,
        send_email=False,
        **mock_kwargs,
    )

    mock_get_image_info.assert_called_once_with(image_name_list)

    mock_print_email_params.assert_called_once_with(
        "mailing list email",
        mock_get_created_images_plaintext.return_value,
    )
