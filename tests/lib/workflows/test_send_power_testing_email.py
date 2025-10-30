from unittest.mock import NonCallableMock, call, patch

import pytest
from apis.email_api.structs.email_params import EmailParams
from apis.email_api.structs.smtp_account import SMTPAccount
from workflows.send_power_testing_email import (
    build_email_params,
    send_power_testing_email,
    validate_input_arguments,
)


def test_validate_input_arguments_empty_flavors():
    """Tests that validate_input_arguments raises error when passed empty flavor name list."""
    with pytest.raises(
        RuntimeError, match="please provide a list of flavor names to decommission"
    ):
        validate_input_arguments([], from_projects=["proj1"])


def test_validate_input_arguments_projects_and_all_projects():
    """Tests that validate_input_arguments raises error when both from_projects and all_projects are True."""
    with pytest.raises(
        RuntimeError,
        match="given both project list and all_projects flag - please choose only one",
    ):
        validate_input_arguments(
            ["flavor1"], from_projects=["proj1"], all_projects=True
        )


def test_validate_input_arguments_no_projects_or_all_projects():
    """Tests that validate_input_arguments raises error when neither from_projects nor all_projects are provided."""
    with pytest.raises(
        RuntimeError,
        match="please provide either a list of project identifiers or the 'all_projects' flag",
    ):
        validate_input_arguments(["flavor1"], from_projects=None, all_projects=False)


def test_validate_input_arguments_valid_all_projects():
    """Tests that validate_input_arguments does not raise an error for a valid input with all_projects flag."""
    try:
        validate_input_arguments(
            flavor_name_list=["flavor1", "flavor2"],
            all_projects=True,
        )
    except RuntimeError as e:
        pytest.fail(f"validate_input_arguments raised an unexpected error: {e}")


def test_validate_input_arguments_valid_projects():
    """Tests that validate_input_arguments does not raise an error for a valid input with a project list."""
    try:
        validate_input_arguments(
            flavor_name_list=["flavor1", "flavor2"],
            from_projects=["proj1", "proj2"],
        )
    except RuntimeError as e:
        pytest.fail(f"validate_input_arguments raised an unexpected error: {e}")


@patch("workflows.send_power_testing_email.EmailTemplateDetails")
@patch("workflows.send_power_testing_email.EmailParams")
def test_build_email_params(mock_email_params, mock_email_template_details):
    """
    Test build_email_params() function constructs EmailParams with correct templates and parameters.
    """
    user_name = "abc111111"
    affected_flavors_table = "Flavor Table HTML"
    affected_servers_table = "Server Table HTML"
    email_kwargs = {"subject": "Power Testing Notice", "email_to": ["test@example.com"]}

    res = build_email_params(
        user_name, affected_flavors_table, affected_servers_table, **email_kwargs
    )

    expected_body_params = {
        "user_name": user_name,
        "affected_flavors_table": affected_flavors_table,
        "affected_servers_table": affected_servers_table,
    }
    mock_email_template_details.assert_has_calls(
        [
            call(template_name="power_testing", template_params=expected_body_params),
            call(template_name="footer", template_params={}),
        ]
    )

    expected_email_templates = [
        mock_email_template_details.return_value,
        mock_email_template_details.return_value,
    ]
    mock_email_params.assert_called_once_with(
        email_templates=expected_email_templates,
        **email_kwargs,
    )

    assert res == mock_email_params.return_value


@patch("workflows.send_power_testing_email.validate_input_arguments")
@patch("workflows.send_power_testing_email.find_servers_with_decom_flavors")
@patch("workflows.send_power_testing_email.find_user_info")
@patch("workflows.send_power_testing_email.tabulate")
@patch("workflows.send_power_testing_email.build_email_params")
@patch("workflows.send_power_testing_email.Emailer")
def test_send_power_testing_email_send_html_cc(
    mock_emailer,
    mock_build_email_params,
    mock_tabulate,
    mock_find_user_info,
    mock_find_servers,
    mock_validate_input_arguments,
):
    """
    Tests send_power_testing_email() function to ensure emails are sent (HTML format) with CC enabled.
    """
    flavor_name_list = ["flavor.small", "flavor.medium"]
    limit_by_projects = ["exampleproject-id"]
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock(spec=SMTPAccount)

    mock_kwargs = {"subject": "Testing Subject"}
    override_email = "test-override@stfc.ac.uk"

    mock_query = mock_find_servers.return_value
    mock_query.to_props.return_value = {
        "user_id1": [],
        "user_id2": [],
    }
    mock_find_user_info.side_effect = [
        ("User One", "user1@example.com"),
        ("User Two", "user2@example.com"),
    ]
    mock_tabulate.side_effect = [
        "HTML Flavor Table 1",
        "HTML Flavor Table 2",
    ]
    mock_query.to_html.side_effect = [
        "User1 Server Table HTML",
        "User2 Server Table HTML",
    ]
    mock_email_params = NonCallableMock(spec=EmailParams)
    mock_build_email_params.return_value = mock_email_params

    send_power_testing_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        flavor_name_list=flavor_name_list,
        limit_by_projects=limit_by_projects,
        all_projects=False,
        as_html=True,
        send_email=True,
        use_override=False,
        override_email_address=override_email,
        cc_cloud_support=True,
        **mock_kwargs,
    )

    mock_validate_input_arguments.assert_called_once_with(
        flavor_name_list, limit_by_projects, False
    )
    mock_find_servers.assert_called_once_with(
        cloud_account, flavor_name_list, limit_by_projects
    )
    mock_query.to_props.assert_called_once()
    mock_find_user_info.assert_has_calls(
        [
            call("user_id1", cloud_account, override_email),
            call("user_id2", cloud_account, override_email),
        ]
    )

    expected_tabulate_data = [{"Flavor": flavor} for flavor in flavor_name_list]
    mock_tabulate.assert_has_calls(
        [
            call(expected_tabulate_data, headers="keys", tablefmt="html"),
            call(expected_tabulate_data, headers="keys", tablefmt="html"),
        ]
    )

    mock_query.to_html.assert_has_calls(
        [
            call(groups=["user_id1"]),
            call(groups=["user_id2"]),
        ]
    )
    mock_query.to_string.assert_not_called()

    mock_build_email_params.assert_has_calls(
        [
            call(
                user_name="User One",
                affected_flavors_table="HTML Flavor Table 1",
                affected_servers_table="User1 Server Table HTML",
                email_to=["user1@example.com"],
                as_html=True,
                email_cc=("cloud-support@stfc.ac.uk",),
                subject="Testing Subject",
            ),
            call(
                user_name="User Two",
                affected_flavors_table="HTML Flavor Table 2",
                affected_servers_table="User2 Server Table HTML",
                email_to=["user2@example.com"],
                as_html=True,
                email_cc=("cloud-support@stfc.ac.uk",),
                subject="Testing Subject",
            ),
        ]
    )

    assert mock_emailer.call_count == 2
    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call(smtp_account),
        ],
        any_order=True,
    )

    mock_emailer.return_value.send_emails.assert_has_calls(
        [
            call([mock_email_params]),
            call([mock_email_params]),
        ],
        any_order=False,
    )
    mock_emailer.return_value.print_email.assert_not_called()


@patch("workflows.send_power_testing_email.validate_input_arguments")
@patch("workflows.send_power_testing_email.find_servers_with_decom_flavors")
@patch("workflows.send_power_testing_email.find_user_info")
@patch("workflows.send_power_testing_email.tabulate")
@patch("workflows.send_power_testing_email.build_email_params")
@patch("workflows.send_power_testing_email.Emailer")
def test_send_power_testing_email_print_plaintext_override(
    mock_emailer,
    mock_build_email_params,
    mock_tabulate,
    mock_find_user_info,
    mock_find_servers,
    mock_validate_input_arguments,
):
    """
    Tests send_power_testing_email() function to ensure content is printed (Plaintext format)
    and uses the override email address.
    """
    flavor_name_list = ["flavor.xlarge"]
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock(spec=SMTPAccount)
    override_email = "override-test@stfc.ac.uk"

    mock_query = mock_find_servers.return_value
    mock_query.to_props.return_value = {
        "user_id3": [],
    }
    mock_find_user_info.return_value = ("User Three", "user3@private.com")

    mock_tabulate.return_value = "Plaintext Flavor Table"
    mock_query.to_string.return_value = "User3 Server Table Plaintext"
    mock_email_params = NonCallableMock(spec=EmailParams)
    mock_build_email_params.return_value = mock_email_params

    send_power_testing_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        flavor_name_list=flavor_name_list,
        limit_by_projects=None,
        all_projects=True,
        as_html=False,
        send_email=False,
        use_override=True,
        override_email_address=override_email,
        cc_cloud_support=False,
    )

    mock_validate_input_arguments.assert_called_once_with(flavor_name_list, None, True)
    mock_find_servers.assert_called_once_with(cloud_account, flavor_name_list, None)
    mock_query.to_props.assert_called_once()
    mock_find_user_info.assert_called_once_with(
        "user_id3", cloud_account, override_email
    )

    expected_tabulate_data = [{"Flavor": flavor} for flavor in flavor_name_list]
    mock_tabulate.assert_called_once_with(
        expected_tabulate_data, headers="keys", tablefmt="grid"
    )

    mock_query.to_string.assert_called_once_with(groups=["user_id3"])
    mock_query.to_html.assert_not_called()

    mock_build_email_params.assert_called_once_with(
        user_name="User Three",
        affected_flavors_table="Plaintext Flavor Table",
        affected_servers_table="User3 Server Table Plaintext",
        email_to=[override_email],
        as_html=False,
        email_cc=None,
    )

    mock_emailer.assert_called_once_with(smtp_account)
    mock_emailer.return_value.print_email.assert_called_once_with(mock_email_params)
    mock_emailer.return_value.send_emails.assert_not_called()
