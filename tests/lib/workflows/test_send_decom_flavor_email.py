from unittest.mock import NonCallableMock, call, patch

import pytest
from workflows.send_decom_flavor_email import (
    build_email_params,
    find_user_info,
    get_affected_flavors_html,
    get_affected_flavors_plaintext,
    print_email_params,
    send_decom_flavor_email,
    validate_flavor_input,
)


def test_get_affected_flavors_html():
    """
    Tests that get_affected_flavors_html returns a html formatted list given valid inputs
    """
    res = get_affected_flavors_html(
        ["flavor1", "flavor2"], ["2024/06/30", "2024/06/29"]
    )
    assert res == (
        "<table>"
        "<tr><th>Affected Flavors</th><th>EOL Date</th></tr>"
        "<tr><td>flavor1</td><td>2024/06/30</td></tr>"
        "<tr><td>flavor2</td><td>2024/06/29</td></tr>"
        "</table>"
    )


@patch("workflows.send_decom_flavor_email.tabulate")
def test_get_affected_flavors_plaintext(mock_tabulate):
    """
    Tests that get_affected_flavors_plaintext calls tabulate correctly
    """
    mock_flavor_list = ["flavor1", "flavor2"]
    mock_eol_list = ["2024/06/30", "2024/06/29"]
    res = get_affected_flavors_plaintext(mock_flavor_list, mock_eol_list)
    mock_tabulate.assert_called_once_with(
        [
            {"Flavor": "flavor1", "EOL Date": "2024/06/30"},
            {"Flavor": "flavor2", "EOL Date": "2024/06/29"},
        ],
        headers="keys",
        tablefmt="plain",
    )
    assert res == mock_tabulate.return_value


def test_validate_flavor_input_empty_flavors():
    """Tests that validate_flavor_input raises error when passed empty flavor name list"""
    with pytest.raises(RuntimeError):
        validate_flavor_input([], ["2024/01/01"])


def test_validate_flavor_input_eol_list_unequal():
    """Tests that validate_flavor_input raises error when lists passed are unequal (eol)"""
    with pytest.raises(RuntimeError):
        validate_flavor_input(["flavor1"], [])

    with pytest.raises(RuntimeError):
        validate_flavor_input(["flavor1", "flavor2"], ["2024/01/01"])


def test_validate_flavor_input_eol_invalid_format():
    """Tests that validate_flavor_input returns error when eol not passed as YYYY/MM/DD"""
    with pytest.raises(RuntimeError):
        validate_flavor_input(["flavor1"], ["24th June 2024"])


def test_validate_flavor_input_projects_and_all_projects():
    """Tests that validate_flavor_input raises error when both projects and all_projects are provided"""
    with pytest.raises(RuntimeError):
        validate_flavor_input(
            ["flavor1"], ["2024/01/01"], from_projects=["proj1"], all_projects=True
        )


def test_validate_flavor_input_no_projects_or_all_projects():
    """Tests that validate_flavor_input raises error when neither projects nor all_projects are provided"""
    with pytest.raises(RuntimeError):
        validate_flavor_input(
            ["flavor1"], ["2024/01/01"], from_projects=None, all_projects=False
        )


def test_validate_flavor_input_valid_all_projects():
    """
    Tests that validate_flavor_input does not raise an error for a valid input with all_projects flag.
    """
    try:
        validate_flavor_input(
            flavor_name_list=["flavor1", "flavor2"],
            flavor_eol_list=["2024/01/01", "2024/06/30"],
            all_projects=True,
        )
    except RuntimeError as e:
        pytest.fail(f"validate_flavor_input raised an unexpected error: {e}")


def test_validate_flavor_input_valid_projects():
    """
    Tests that validate_flavor_input does not raise an error for a valid input with a project list.
    """
    try:
        validate_flavor_input(
            flavor_name_list=["flavor1", "flavor2"],
            flavor_eol_list=["2024/01/01", "2024/06/30"],
            from_projects=["proj1", "proj2"],
        )
    except RuntimeError as e:
        pytest.fail(f"validate_flavor_input raised an unexpected error: {e}")


@patch("workflows.send_decom_flavor_email.validate_flavor_input")
@patch("workflows.send_decom_flavor_email.find_servers_with_flavors")
def test_send_decom_flavor_email_no_servers_found(
    mock_find_servers,
    mock_validate_flavor_input,
):
    """
    Tests that send_decom_flavor_email raises RuntimeError when no servers
    are found with the specified flavors.
    """
    flavor_name_list = ["flavor1", "flavor2"]
    flavor_eol_list = ["2024/01/01", "2024/06/30"]
    limit_by_projects = ["project1", "project2"]
    all_projects = False
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()

    mock_query = mock_find_servers.return_value
    mock_query.to_props.return_value = {}

    with pytest.raises(RuntimeError) as exc_info:
        send_decom_flavor_email(
            smtp_account=smtp_account,
            cloud_account=cloud_account,
            flavor_name_list=flavor_name_list,
            flavor_eol_list=flavor_eol_list,
            limit_by_projects=limit_by_projects,
            all_projects=all_projects,
            as_html=False,
            send_email=True,
            use_override=False,
        )

    mock_validate_flavor_input.assert_called_once_with(
        flavor_name_list, flavor_eol_list, limit_by_projects, all_projects
    )
    mock_find_servers.assert_called_once_with(
        cloud_account, flavor_name_list, limit_by_projects
    )
    mock_query.to_props.assert_called()

    assert "No servers found with flavors flavor1, flavor2" in str(exc_info.value)
    assert "project1,project2" in str(exc_info.value)


# pylint:disable=too-many-locals
@patch("workflows.send_decom_flavor_email.UserQuery")
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
    mock_user_query.return_value.select.assert_called_once_with(
        "user_name", "user_email"
    )
    mock_user_query.return_value.where.assert_called_once_with(
        "equal_to", "user_id", value=mock_user_id
    )
    mock_user_query.return_value.run.assert_called_once_with(
        cloud_account=mock_cloud_account
    )
    mock_user_query.return_value.to_props.assert_called_once_with(flatten=True)

    assert res[0] == "foo"
    assert res[1] == "foo@example.com"


@patch("workflows.send_decom_flavor_email.UserQuery")
def test_find_user_info_invalid(mock_user_query):
    """
    Tests find_user_info where query is given a invalid user id
    """
    mock_user_id = NonCallableMock()
    mock_cloud_account = NonCallableMock()
    mock_override_email = NonCallableMock()
    mock_user_query.return_value.to_props.return_value = []
    res = find_user_info(mock_user_id, mock_cloud_account, mock_override_email)
    mock_user_query.assert_called_once()
    mock_user_query.return_value.select.assert_called_once_with(
        "user_name", "user_email"
    )
    mock_user_query.return_value.where.assert_called_once_with(
        "equal_to", "user_id", value=mock_user_id
    )
    mock_user_query.return_value.run.assert_called_once_with(
        cloud_account=mock_cloud_account
    )
    mock_user_query.return_value.to_props.assert_called_once_with(flatten=True)

    assert res[0] == ""
    assert res[1] == mock_override_email


@patch("workflows.send_decom_flavor_email.UserQuery")
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
    mock_user_query.return_value.select.assert_called_once_with(
        "user_name", "user_email"
    )
    mock_user_query.return_value.where.assert_called_once_with(
        "equal_to", "user_id", value=mock_user_id
    )
    mock_user_query.return_value.run.assert_called_once_with(
        cloud_account=mock_cloud_account
    )
    mock_user_query.return_value.to_props.assert_called_once_with(flatten=True)

    assert res[0] == ""
    assert res[1] == mock_override_email


def test_print_email_params():
    """
    Test print_email_params() function simply prints values
    """
    email_addr = "test@example.com"
    user_name = "John Doe"
    as_html = True
    flavor_table = "Flavor Table Content"
    decom_table = "Decom Table Content"

    with patch("builtins.print") as mock_print:
        print_email_params(email_addr, user_name, as_html, flavor_table, decom_table)

    mock_print.assert_called_once_with(
        f"Send Email To: {email_addr}\n"
        f"email_templates decom-email: username {user_name}\n"
        f"send as html: {as_html}\n"
        f"flavor table: {flavor_table}\n"
        f"decom table: {decom_table}\n"
    )


@patch("workflows.send_decom_flavor_email.EmailTemplateDetails")
@patch("workflows.send_decom_flavor_email.EmailParams")
def test_build_params(mock_email_params, mock_email_template_details):
    """
    Test build_params() function creates email params appropriately and returns them
    """

    user_name = "John Doe"
    flavor_table = "Flavor Table Content"
    decom_table = "Decom Table Content"
    email_kwargs = {"arg1": "val1", "arg2": "val2"}

    res = build_email_params(user_name, flavor_table, decom_table, **email_kwargs)
    mock_email_template_details.assert_has_calls(
        [
            call(
                template_name="decom_flavor",
                template_params={
                    "username": user_name,
                    "affected_flavors_table": flavor_table,
                    "decom_table": decom_table,
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
@patch("workflows.send_decom_flavor_email.validate_flavor_input")
@patch("workflows.send_decom_flavor_email.find_servers_with_flavors")
@patch("workflows.send_decom_flavor_email.find_user_info")
@patch("workflows.send_decom_flavor_email.get_affected_flavors_plaintext")
@patch("workflows.send_decom_flavor_email.build_email_params")
@patch("workflows.send_decom_flavor_email.Emailer")
def test_send_decom_flavor_email_send_plaintext(
    mock_emailer,
    mock_build_email_params,
    mock_get_affected_flavors_plaintext,
    mock_find_user_info,
    mock_find_servers,
    mock_validate_flavor_input,
):
    """
    Tests send_decom_flavor_email() function actually sends email - as_html false
    """
    flavor_name_list = ["flavor1", "flavor2"]
    flavor_eol_list = NonCallableMock()
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

    send_decom_flavor_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        flavor_name_list=flavor_name_list,
        flavor_eol_list=flavor_eol_list,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=False,
        send_email=True,
        use_override=False,
        **mock_kwargs,
    )

    mock_validate_flavor_input.assert_called_once_with(
        flavor_name_list, flavor_eol_list, limit_by_projects, all_projects
    )
    mock_find_servers.assert_called_once_with(
        cloud_account, flavor_name_list, limit_by_projects
    )
    mock_query.to_props.assert_called()
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
                mock_get_affected_flavors_plaintext.return_value,
                mock_query.to_string.return_value,
                email_to=["user_email1"],
                as_html=False,
                email_cc=None,
                **mock_kwargs,
            ),
            call(
                "user2",
                mock_get_affected_flavors_plaintext.return_value,
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
            call(groups=["user_id1"]),
            call(groups=["user_id2"]),
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
@patch("workflows.send_decom_flavor_email.validate_flavor_input")
@patch("workflows.send_decom_flavor_email.find_servers_with_flavors")
@patch("workflows.send_decom_flavor_email.find_user_info")
@patch("workflows.send_decom_flavor_email.get_affected_flavors_html")
@patch("workflows.send_decom_flavor_email.build_email_params")
@patch("workflows.send_decom_flavor_email.Emailer")
def test_send_decom_flavor_email_send_html(
    mock_emailer,
    mock_build_email_params,
    mock_get_affected_flavors_html,
    mock_find_user_info,
    mock_find_servers,
    mock_validate_flavor_input,
):
    """
    Tests send_decom_flavor_email() function actually sends email - as_html True
    """

    flavor_name_list = ["flavor1", "flavor2"]
    flavor_eol_list = NonCallableMock()
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

    send_decom_flavor_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        flavor_name_list=flavor_name_list,
        flavor_eol_list=flavor_eol_list,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=True,
        send_email=True,
        use_override=False,
        **mock_kwargs,
    )

    mock_validate_flavor_input.assert_called_once_with(
        flavor_name_list, flavor_eol_list, limit_by_projects, all_projects
    )
    mock_find_servers.assert_called_once_with(
        cloud_account, flavor_name_list, limit_by_projects
    )
    mock_query.to_props.assert_called()
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
                mock_get_affected_flavors_html.return_value,
                mock_query.to_html.return_value,
                email_to=["user_email1"],
                as_html=True,
                email_cc=None,
                **mock_kwargs,
            ),
            call(
                "user2",
                mock_get_affected_flavors_html.return_value,
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
            call(groups=["user_id1"]),
            call(groups=["user_id2"]),
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


@patch("workflows.send_decom_flavor_email.validate_flavor_input")
@patch("workflows.send_decom_flavor_email.find_servers_with_flavors")
@patch("workflows.send_decom_flavor_email.find_user_info")
@patch("workflows.send_decom_flavor_email.get_affected_flavors_plaintext")
@patch("workflows.send_decom_flavor_email.print_email_params")
def test_send_decom_flavor_email_print(
    mock_print_email_params,
    mock_get_affected_flavors_plaintext,
    mock_find_user_info,
    mock_find_servers,
    mock_validate_flavor_input,
):
    """
    Tests send_decom_flavor_email() function prints when send_email=False
    """

    flavor_name_list = ["flavor1", "flavor2"]
    flavor_eol_list = NonCallableMock()
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

    send_decom_flavor_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        flavor_name_list=flavor_name_list,
        flavor_eol_list=flavor_eol_list,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=False,
        send_email=False,
        use_override=False,
        **mock_kwargs,
    )

    mock_validate_flavor_input.assert_called_once_with(
        flavor_name_list, flavor_eol_list, limit_by_projects, all_projects
    )
    mock_find_servers.assert_called_once_with(
        cloud_account, flavor_name_list, limit_by_projects
    )
    mock_query.to_props.assert_called()
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
                mock_get_affected_flavors_plaintext.return_value,
                mock_query.to_string.return_value,
            ),
            call(
                "user_email2",
                "user2",
                False,
                mock_get_affected_flavors_plaintext.return_value,
                mock_query.to_string.return_value,
            ),
        ]
    )


@patch("workflows.send_decom_flavor_email.validate_flavor_input")
@patch("workflows.send_decom_flavor_email.find_servers_with_flavors")
@patch("workflows.send_decom_flavor_email.find_user_info")
@patch("workflows.send_decom_flavor_email.get_affected_flavors_plaintext")
@patch("workflows.send_decom_flavor_email.build_email_params")
@patch("workflows.send_decom_flavor_email.Emailer")
def test_send_decom_flavor_email_use_override(
    mock_emailer,
    mock_build_email_params,
    mock_get_affected_flavors_plaintext,
    mock_find_user_info,
    mock_find_servers,
    mock_validate_flavor_input,
):
    """
    Tests that send_decom_flavor_email sends to the override email address
    when the use_override flag is set.
    """
    flavor_name_list = ["flavor1", "flavor2"]
    flavor_eol_list = ["2024/01/01", "2024/06/30"]
    limit_by_projects = ["project1"]
    all_projects = False
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    override_email = "test-override@stfc.ac.uk"

    mock_query = mock_find_servers.return_value
    mock_query.to_props.return_value = {
        "user_id1": [],
    }
    mock_find_user_info.return_value = ("user1", "user1@example.com")

    send_decom_flavor_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        flavor_name_list=flavor_name_list,
        flavor_eol_list=flavor_eol_list,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=False,
        send_email=True,
        use_override=True,
        override_email_address=override_email,
        cc_cloud_support=False,
    )

    mock_validate_flavor_input.assert_called_once_with(
        flavor_name_list, flavor_eol_list, limit_by_projects, all_projects
    )
    mock_find_servers.assert_called_once_with(
        cloud_account, flavor_name_list, limit_by_projects
    )
    mock_query.to_props.assert_called()
    mock_find_user_info.assert_called_once_with(
        "user_id1", cloud_account, override_email
    )

    mock_build_email_params.assert_called_once_with(
        "user1",
        mock_get_affected_flavors_plaintext.return_value,
        mock_query.to_string.return_value,
        email_to=[override_email],
        as_html=False,
        email_cc=None,
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )
