from unittest.mock import patch, call, NonCallableMock

import pytest
from workflows.send_down_disabled_hypervisors_email import (
    print_email_params,
    build_email_params,
    send_down_disabled_hypervisors_email,
)


def test_print_email_params():
    """
    Test print_email_params() function simply prints values
    """
    email_addr = "test@example.com"
    as_html = True
    down_table = "Down Table Content"
    disabled_table = "Disabled Table Content"

    with patch("builtins.print") as mock_print:
        print_email_params(email_addr, as_html, down_table, disabled_table)

    mock_print.assert_called_once_with(
        f"Send Email To: {email_addr}\n"
        f"send as html: {as_html}\n"
        f"down hypervisors table:\n{down_table}\n"
        f"disabled hypervisors table:\n{disabled_table}\n"
    )


@patch("workflows.send_down_disabled_hypervisors_email.EmailTemplateDetails")
@patch("workflows.send_down_disabled_hypervisors_email.EmailParams")
def test_build_params(mock_email_params, mock_email_template_details):
    """
    Test build_params() function creates email params appropriately and returns them
    """

    down_table = "Down Table Content"
    disabled_table = "Disabled Table Content"
    email_kwargs = {"arg1": "val1", "arg2": "val2"}

    res = build_email_params(down_table, disabled_table, **email_kwargs)
    mock_email_template_details.assert_has_calls(
        [
            call(
                template_name="hypervisor_down_disabled",
                template_params={
                    "down_table": down_table,
                    "disabled_table": disabled_table,
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


# pylint:disable=too-many-arguments
@patch("workflows.send_down_disabled_hypervisors_email.find_down_hypervisors")
@patch("workflows.send_down_disabled_hypervisors_email.find_disabled_hypervisors")
@patch("workflows.send_down_disabled_hypervisors_email.build_email_params")
@patch("workflows.send_down_disabled_hypervisors_email.Emailer")
def test_send_down_disabled_hypervisors_email_plaintext(
    mock_emailer,
    mock_build_email_params,
    mock_find_disabled_hypervisors,
    mock_find_down_hypervisors,
):
    """
    Tests send_down_disabled_hypervisors_email() function actually sends email - as_html False
    """
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_down_query = mock_find_down_hypervisors.return_value
    mock_disabled_query = mock_find_disabled_hypervisors.return_value

    # doesn't matter what the values are here since we're just getting the keys

    send_down_disabled_hypervisors_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        as_html=False,
        send_email=True,
        use_override=False,
        **mock_kwargs,
    )

    mock_find_down_hypervisors.assert_called_once_with(cloud_account)
    mock_find_disabled_hypervisors.assert_called_once_with(cloud_account)

    mock_build_email_params.assert_has_calls(
        [
            call(
                mock_down_query.to_string.return_value,
                mock_disabled_query.to_string.return_value,
                email_to=["ops-team"],
                as_html=False,
                email_cc=None,
                **mock_kwargs,
            ),
        ]
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )


# pylint:disable=too-many-arguments
@patch("workflows.send_down_disabled_hypervisors_email.find_down_hypervisors")
@patch("workflows.send_down_disabled_hypervisors_email.find_disabled_hypervisors")
@patch("workflows.send_down_disabled_hypervisors_email.build_email_params")
@patch("workflows.send_down_disabled_hypervisors_email.Emailer")
def test_send_down_disabled_hypervisors_email_send_html(
    mock_emailer,
    mock_build_email_params,
    mock_find_disabled_hypervisors,
    mock_find_down_hypervisors,
):
    """
    Tests send_down_disabled_hypervisors_email() function actually sends email - as_html True
    """
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_down_query = mock_find_down_hypervisors.return_value
    mock_disabled_query = mock_find_disabled_hypervisors.return_value

    # doesn't matter what the values are here since we're just getting the keys

    send_down_disabled_hypervisors_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        as_html=True,
        send_email=True,
        use_override=False,
        **mock_kwargs,
    )

    mock_find_down_hypervisors.assert_called_once_with(cloud_account)
    mock_find_disabled_hypervisors.assert_called_once_with(cloud_account)

    mock_build_email_params.assert_has_calls(
        [
            call(
                mock_down_query.to_html.return_value,
                mock_disabled_query.to_html.return_value,
                email_to=["ops-team"],
                as_html=True,
                email_cc=None,
                **mock_kwargs,
            ),
        ]
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )


# pylint:disable=too-many-arguments
@patch("workflows.send_down_disabled_hypervisors_email.find_down_hypervisors")
@patch("workflows.send_down_disabled_hypervisors_email.find_disabled_hypervisors")
@patch("workflows.send_down_disabled_hypervisors_email.print_email_params")
def test_send_down_disabled_hypervisors_email_print(
    mock_print_email_params,
    mock_find_disabled_hypervisors,
    mock_find_down_hypervisors,
):
    """
    Tests send_down_disabled_hypervisors_email() function prints when send_email=False
    """
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_down_query = mock_find_down_hypervisors.return_value
    mock_disabled_query = mock_find_disabled_hypervisors.return_value

    # doesn't matter what the values are here since we're just getting the keys

    send_down_disabled_hypervisors_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        as_html=False,
        send_email=False,
        use_override=False,
        **mock_kwargs,
    )

    mock_find_down_hypervisors.assert_called_once_with(cloud_account)
    mock_find_disabled_hypervisors.assert_called_once_with(cloud_account)

    mock_print_email_params.assert_has_calls(
        [
            call(
                "ops-team",
                False,
                mock_down_query.to_string.return_value,
                mock_disabled_query.to_string.return_value,
            ),
        ]
    )


# pylint:disable=too-many-arguments
@patch("workflows.send_down_disabled_hypervisors_email.find_down_hypervisors")
@patch("workflows.send_down_disabled_hypervisors_email.find_disabled_hypervisors")
@patch("workflows.send_down_disabled_hypervisors_email.build_email_params")
@patch("workflows.send_down_disabled_hypervisors_email.Emailer")
def test_send_down_disabled_hypervisors_email_use_override(
    mock_emailer,
    mock_build_email_params,
    mock_find_disabled_hypervisors,
    mock_find_down_hypervisors,
):
    """
    Tests send_down_disabled_hypervisors_email() function actually sends email - as_html True
    """
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}
    override_email_address = "example@example.com"

    mock_down_query = mock_find_down_hypervisors.return_value
    mock_disabled_query = mock_find_disabled_hypervisors.return_value

    # doesn't matter what the values are here since we're just getting the keys

    send_down_disabled_hypervisors_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        as_html=False,
        send_email=True,
        use_override=True,
        override_email_address="example@example.com",
        **mock_kwargs,
    )

    mock_find_down_hypervisors.assert_called_once_with(cloud_account)
    mock_find_disabled_hypervisors.assert_called_once_with(cloud_account)

    mock_build_email_params.assert_has_calls(
        [
            call(
                mock_down_query.to_string.return_value,
                mock_disabled_query.to_string.return_value,
                email_to=[override_email_address],
                as_html=False,
                email_cc=None,
                **mock_kwargs,
            ),
        ]
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )


@patch("workflows.send_down_disabled_hypervisors_email.find_down_hypervisors")
@patch("workflows.send_down_disabled_hypervisors_email.find_disabled_hypervisors")
def test_send_down_disabled_hypervisors_no_hypervisors_found(
    mock_find_disabled_hypervisors,
    mock_find_down_hypervisors,
):

    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_down_query = mock_find_down_hypervisors.return_value
    mock_disabled_query = mock_find_disabled_hypervisors.return_value

    with pytest.raises(RuntimeError):
        send_down_disabled_hypervisors_email(
            smtp_account=smtp_account,
            cloud_account=cloud_account,
            as_html=False,
            send_email=False,
            use_override=False,
            **mock_kwargs,
        )
