from unittest.mock import patch, call, NonCallableMock
import pytest

from workflows.send_shutoff_vm_email import (
    find_servers_with_shutoff_vms,
    print_email_params,
    build_email_params,
    find_user_info,
    send_shutoff_vm_email,
)


@patch("workflows.send_shutoff_vm_email.UserQuery")
def test_find_user_info_valid(mock_user_query):
    """
    Tests find_user_info where query is given a valid user id
    """
    mock_user_id = NonCallableMock()
    mock_cloud_account = NonCallableMock()
    mock_override_email = NonCallableMock()
    mock_user_query.return_value.to_props.return_value = {
        "user_name": ["foo"],
        "user_email": ["foo@example.com"],
    }
    res = find_user_info(mock_user_id, mock_cloud_account, mock_override_email)
    mock_user_query.assert_called_once()
    mock_user_query.return_value.select.assert_called_once_with("name", "email_address")
    mock_user_query.return_value.where.assert_called_once_with(
        "equal_to", "id", value=mock_user_id
    )
    mock_user_query.return_value.run.assert_called_once_with(
        cloud_account=mock_cloud_account
    )
    mock_user_query.return_value.to_props.assert_called_once_with(flatten=True)

    assert res[0] == "foo"
    assert res[1] == "foo@example.com"


@patch("workflows.send_shutoff_vm_email.UserQuery")
def test_find_user_info_invalid(mock_user_query):
    """
    Tests find_user_info where query is given an invalid user id
    """
    mock_user_id = NonCallableMock()
    mock_cloud_account = NonCallableMock()
    mock_override_email = NonCallableMock()
    mock_user_query.return_value.to_props.return_value = []
    res = find_user_info(mock_user_id, mock_cloud_account, mock_override_email)
    mock_user_query.assert_called_once()
    mock_user_query.return_value.select.assert_called_once_with("name", "email_address")
    mock_user_query.return_value.where.assert_called_once_with(
        "equal_to", "id", value=mock_user_id
    )
    mock_user_query.return_value.run.assert_called_once_with(
        cloud_account=mock_cloud_account
    )
    mock_user_query.return_value.to_props.assert_called_once_with(flatten=True)

    assert res[0] == ""
    assert res[1] == mock_override_email


@patch("workflows.send_shutoff_vm_email.UserQuery")
def test_find_user_info_no_email_address(mock_user_query):
    """
    Tests find_user_info where query result contains no email address
    """
    mock_user_id = NonCallableMock()
    mock_cloud_account = NonCallableMock()
    mock_override_email = NonCallableMock()
    mock_user_query.return_value.to_props.return_value = {
        "user_id": ["foo"],
        "user_email": [None],
    }
    res = find_user_info(mock_user_id, mock_cloud_account, mock_override_email)
    mock_user_query.assert_called_once()
    mock_user_query.return_value.select.assert_called_once_with("name", "email_address")
    mock_user_query.return_value.where.assert_called_once_with(
        "equal_to", "id", value=mock_user_id
    )
    mock_user_query.return_value.run.assert_called_once_with(
        cloud_account=mock_cloud_account
    )
    mock_user_query.return_value.to_props.assert_called_once_with(flatten=True)

    assert res[0] == ""
    assert res[1] == mock_override_email


@patch("workflows.send_shutoff_vm_email.ServerQuery")
def test_find_servers_with_shutoff_vms_valid(mock_server_query):
    """
    Tests find_servers_with_shutoff_vms() function
    """
    mock_server_query_obj = mock_server_query.return_value

    res = find_servers_with_shutoff_vms("test-cloud-account", ["project1", "project2"])

    mock_server_query_obj.run.assert_called_once_with(
        "test-cloud-account",
        as_admin=False,
        from_projects=["project1", "project2"],
        all_projects=False,
    )
    mock_server_query_obj.select.assert_called_once_with("id", "name", "addresses")
    mock_server_query_obj.to_props.assert_called_once()

    mock_server_query_obj.append_from.assert_called_once_with(
        "PROJECT_QUERY", "test-cloud-account", "name"
    )
    mock_server_query_obj.group_by.assert_called_once_with("user_id")
    assert res == mock_server_query_obj


@patch("workflows.send_shutoff_vm_email.ServerQuery")
def test_find_servers_with_shutoff_vms_no_servers_found(mock_server_query):
    """
    Tests that find_servers_with_shutoff_vms fails when provided
    """
    mock_server_query_obj = mock_server_query.return_value
    mock_server_query_obj.to_props.return_value = None

    with pytest.raises(RuntimeError):
        find_servers_with_shutoff_vms("test-cloud-account", ["project1", "project2"])

    mock_server_query_obj.run.assert_called_once_with(
        "test-cloud-account",
        as_admin=False,
        from_projects=["project1", "project2"],
        all_projects=False,
    )
    mock_server_query_obj.select.assert_called_once_with("id", "name", "addresses")
    mock_server_query_obj.to_props.assert_called_once()


def test_print_email_params():
    """
    Test print_email_params() function simply prints values
    """
    email_addr = "test@example.com"
    user_name = "John Doe"
    as_html = True
    shutoff_table = "Shutoff Table Content"

    with patch("builtins.print") as mock_print:
        print_email_params(email_addr, user_name, as_html, shutoff_table)

    mock_print.assert_called_once_with(
        f"Send Email To: {email_addr}\n"
        f"email_templates shutoff-email: username {user_name}\n"
        f"send as html: {as_html}\n"
        f"shutoff table: {shutoff_table}\n"
    )


@patch("workflows.send_shutoff_vm_email.EmailTemplateDetails")
@patch("workflows.send_shutoff_vm_email.EmailParams")
def test_build_params(mock_email_params, mock_email_template_details):
    """
    Test build_params() function creates email params appropriately and returns them
    """

    user_name = "John Doe"
    shutoff_table = "Shutoff Table Content"
    email_kwargs = {"arg1": "val1", "arg2": "val2"}

    res = build_email_params(user_name, shutoff_table, **email_kwargs)
    mock_email_template_details.assert_has_calls(
        [
            call(
                template_name="shutoff_vm",
                template_params={
                    "username": user_name,
                    "shutoff_table": shutoff_table,
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
@patch("workflows.send_shutoff_vm_email.find_servers_with_shutoff_vms")
@patch("workflows.send_shutoff_vm_email.find_user_info")
@patch("workflows.send_shutoff_vm_email.build_email_params")
@patch("workflows.send_shutoff_vm_email.Emailer")
def test_send_shutoff_vm_email_send_plaintext(
    mock_emailer,
    mock_build_email_params,
    mock_find_user_info,
    mock_find_servers,
):
    """
    Tests send_shutoff_vm_email() function actually sends email - as_html False
    """
    limit_by_projects = ["project1", "project2"]
    all_projects = False
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_query = mock_find_servers.return_value

    # doesn't matter what the values are here since we're just getting the keys
    mock_query.to_props.return_value = {
        "user_id1": [],
        "user_id2": [],
    }
    mock_find_user_info.side_effect = [
        ("user1", "user_email1"),
        ("user2", "user_email2"),
    ]

    send_shutoff_vm_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=False,
        send_email=True,
        use_override=False,
        **mock_kwargs,
    )

    mock_find_servers.assert_called_once_with(cloud_account, limit_by_projects)
    mock_query.to_props.assert_called_once()
    mock_find_user_info.assert_has_calls(
        [
            call("user_id1", cloud_account, "cloud-support@stfc.ac.uk"),
            call("user_id2", cloud_account, "cloud-support@stfc.ac.uk"),
        ]
    )

    mock_build_email_params.assert_has_calls(
        [
            call(
                "user1",
                mock_query.to_string.return_value,
                email_to=["user_email1"],
                as_html=False,
                email_cc=None,
                **mock_kwargs,
            ),
            call(
                "user2",
                mock_query.to_string.return_value,
                email_to=["user_email2"],
                as_html=False,
                email_cc=None,
                **mock_kwargs,
            ),
        ]
    )

    mock_query.to_string.assert_has_calls(
        [
            call(groups=["user_id1"], include_group_titles=False),
            call(groups=["user_id2"], include_group_titles=False),
        ]
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )


# pylint:disable=too-many-arguments
@patch("workflows.send_shutoff_vm_email.find_servers_with_shutoff_vms")
@patch("workflows.send_shutoff_vm_email.find_user_info")
@patch("workflows.send_shutoff_vm_email.build_email_params")
@patch("workflows.send_shutoff_vm_email.Emailer")
def test_send_shutoff_vm_email_send_html(
    mock_emailer,
    mock_build_email_params,
    mock_find_user_info,
    mock_find_servers,
):
    """
    Tests send_shutoff_vm_email() function actually sends email - as_html True
    """
    limit_by_projects = ["project1", "project2"]
    all_projects = False
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_query = mock_find_servers.return_value

    # doesn't matter what the values are here since we're just getting the keys
    mock_query.to_props.return_value = {
        "user_id1": [],
        "user_id2": [],
    }
    mock_find_user_info.side_effect = [
        ("user1", "user_email1"),
        ("user2", "user_email2"),
    ]

    send_shutoff_vm_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=True,
        send_email=True,
        use_override=False,
        **mock_kwargs,
    )

    mock_find_servers.assert_called_once_with(cloud_account, limit_by_projects)
    mock_query.to_props.assert_called_once()
    mock_find_user_info.assert_has_calls(
        [
            call("user_id1", cloud_account, "cloud-support@stfc.ac.uk"),
            call("user_id2", cloud_account, "cloud-support@stfc.ac.uk"),
        ]
    )

    mock_build_email_params.assert_has_calls(
        [
            call(
                "user1",
                mock_query.to_html.return_value,
                email_to=["user_email1"],
                as_html=True,
                email_cc=None,
                **mock_kwargs,
            ),
            call(
                "user2",
                mock_query.to_html.return_value,
                email_to=["user_email2"],
                as_html=True,
                email_cc=None,
                **mock_kwargs,
            ),
        ]
    )

    mock_query.to_html.assert_has_calls(
        [
            call(groups=["user_id1"], include_group_titles=False),
            call(groups=["user_id2"], include_group_titles=False),
        ]
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )


# pylint:disable=too-many-arguments
@patch("workflows.send_shutoff_vm_email.find_servers_with_shutoff_vms")
@patch("workflows.send_shutoff_vm_email.find_user_info")
@patch("workflows.send_shutoff_vm_email.print_email_params")
def test_send_shutoff_vm_email_print(
    mock_print_email_params,
    mock_find_user_info,
    mock_find_servers,
):
    """
    Tests send_shutoff_vm_email() function prints when send_email=False
    """
    limit_by_projects = ["project1", "project2"]
    all_projects = False
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_query = mock_find_servers.return_value

    # doesn't matter what the values are here since we're just getting the keys
    mock_query.to_props.return_value = {
        "user_id1": [],
        "user_id2": [],
    }
    mock_find_user_info.side_effect = [
        ("user1", "user_email1"),
        ("user2", "user_email2"),
    ]

    send_shutoff_vm_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=False,
        send_email=False,
        use_override=False,
        **mock_kwargs,
    )

    mock_find_servers.assert_called_once_with(cloud_account, limit_by_projects)
    mock_query.to_props.assert_called_once()
    mock_find_user_info.assert_has_calls(
        [
            call("user_id1", cloud_account, "cloud-support@stfc.ac.uk"),
            call("user_id2", cloud_account, "cloud-support@stfc.ac.uk"),
        ]
    )

    mock_print_email_params.assert_has_calls(
        [
            call(
                "user_email1",
                "user1",
                False,
                mock_query.to_string.return_value,
            ),
            call(
                "user_email2",
                "user2",
                False,
                mock_query.to_string.return_value,
            ),
        ]
    )

    mock_query.to_string.assert_has_calls(
        [
            call(groups=["user_id1"], include_group_titles=False),
            call(groups=["user_id2"], include_group_titles=False),
        ]
    )


# pylint:disable=too-many-arguments
@patch("workflows.send_shutoff_vm_email.find_servers_with_shutoff_vms")
@patch("workflows.send_shutoff_vm_email.find_user_info")
@patch("workflows.send_shutoff_vm_email.build_email_params")
@patch("workflows.send_shutoff_vm_email.Emailer")
def test_send_shutoff_vm_email_use_override(
    mock_emailer,
    mock_build_email_params,
    mock_find_user_info,
    mock_find_servers,
):
    """
    Tests send_shutoff_vm_email() function sends email to override email - when use_override set
    """
    limit_by_projects = ["project1", "project2"]
    all_projects = False
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}
    override_email_address = "example@example.com"

    mock_query = mock_find_servers.return_value

    # doesn't matter what the values are here since we're just getting the keys
    mock_query.to_props.return_value = {
        "user_id1": [],
        "user_id2": [],
    }
    mock_find_user_info.side_effect = [
        ("user1", "user_email1"),
        ("user2", "user_email2"),
    ]

    send_shutoff_vm_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=False,
        send_email=True,
        use_override=True,
        override_email_address=override_email_address,
        **mock_kwargs,
    )

    mock_find_servers.assert_called_once_with(cloud_account, limit_by_projects)
    mock_query.to_props.assert_called_once()
    mock_find_user_info.assert_has_calls(
        [
            call("user_id1", cloud_account, override_email_address),
            call("user_id2", cloud_account, override_email_address),
        ]
    )

    mock_build_email_params.assert_has_calls(
        [
            call(
                "user1",
                mock_query.to_string.return_value,
                email_to=[override_email_address],
                as_html=False,
                email_cc=None,
                **mock_kwargs,
            ),
            call(
                "user2",
                mock_query.to_string.return_value,
                email_to=[override_email_address],
                as_html=False,
                email_cc=None,
                **mock_kwargs,
            ),
        ]
    )

    mock_query.to_string.assert_has_calls(
        [
            call(groups=["user_id1"], include_group_titles=False),
            call(groups=["user_id2"], include_group_titles=False),
        ]
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )


def test_raise_error_when_both_from_projects_all_projects():
    """Tests that send_shutoff_vm_email raises error if both from_projects or all_projects given"""
    with pytest.raises(RuntimeError):
        send_shutoff_vm_email(
            smtp_account="",
            cloud_account="",
            all_projects=True,
            limit_by_projects=["proj1", "proj2"],
        )


def test_raise_error_when_neither_from_projects_all_projects():
    """Tests that send_shutoff_vm_email raises error if neither from_projects nor all_projects given"""
    with pytest.raises(RuntimeError):
        send_shutoff_vm_email(
            smtp_account="",
            cloud_account="",
        )
