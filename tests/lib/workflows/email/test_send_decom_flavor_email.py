from unittest.mock import patch, call, NonCallableMock
import pytest


from enums.query.props.flavor_properties import FlavorProperties
from enums.query.props.project_properties import ProjectProperties
from enums.query.props.server_properties import ServerProperties
from enums.query.props.user_properties import UserProperties
from enums.query.query_presets import QueryPresetsGeneric
from enums.query.sort_order import SortOrder
from workflows.email.send_decom_flavor_email import (
    validate,
    find_users_with_decom_flavors,
    print_email_params,
    build_email_params,
    send_decom_flavor_email,
)


def test_validate_flavor_list_empty():
    """Tests that validate raises error when flavor_name_list is empty"""
    with pytest.raises(RuntimeError):
        validate([], from_projects=None, all_projects=True)


def test_validate_not_from_projects_or_all_projects():
    """Tests that validate raises error neither from_projects or all_projects given"""
    with pytest.raises(RuntimeError):
        validate(["flavor1", "flavor2"], from_projects=None, all_projects=False)


def test_validate_empty_from_projects():
    """Tests that validate raises error neither from_projects or all_projects given"""
    with pytest.raises(RuntimeError):
        validate(["flavor1", "flavor2"], from_projects=[], all_projects=False)


def test_validate_from_projects_and_all_projects():
    """Tests that validate raises error when from_projects and all_projects are both given"""
    with pytest.raises(RuntimeError):
        validate(
            ["flavor1", "flavor2"],
            from_projects=["project1", "project2"],
            all_projects=True,
        )


def test_validate_success():
    """
    Tests validate raises no error when flavor list is provided
    and one of either all_projects or from_projects given
    """
    validate(
        ["flavor1", "flavor2"],
        from_projects=["project1", "project2"],
        all_projects=False,
    )
    validate(["flavor1", "flavor2"], from_projects=None, all_projects=True)


# pylint:disable=too-many-locals


@patch("workflows.email.send_decom_flavor_email.FlavorQuery")
def test_find_users_with_decom_flavor(mock_flavor_query):
    """
    Tests find_users_with_decom_flavors() function
    should run a complex FlavorQuery query - chaining into servers, then users and return final query
    """
    res = find_users_with_decom_flavors(
        "test-cloud-account", ["flavor1", "flavor2"], ["project1", "project2"]
    )

    mock_flavor_query.assert_called_once()
    flavor_query_where_1 = mock_flavor_query.return_value.where
    flavor_query_where_1.assert_called_once_with(
        QueryPresetsGeneric.EQUAL_TO,
        FlavorProperties.FLAVOR_IS_PUBLIC,
        value=True,
    )

    flavor_query_where_2 = flavor_query_where_1.return_value.where
    flavor_query_where_2.assert_called_once_with(
        QueryPresetsGeneric.ANY_IN,
        FlavorProperties.FLAVOR_NAME,
        values=["flavor1", "flavor2"],
    )

    flavor_query_run = flavor_query_where_2.return_value.run
    flavor_query_run.assert_called_once_with("test-cloud-account")

    flavor_query_sort_by = flavor_query_run.return_value.sort_by
    flavor_query_sort_by.assert_called_once_with(
        (FlavorProperties.FLAVOR_ID, SortOrder.ASC)
    )

    flavor_query_then = flavor_query_sort_by.return_value.then
    flavor_query_then.assert_called_once_with(
        "SERVER_QUERY", keep_previous_results=True
    )

    server_query_run = flavor_query_then.return_value.run
    server_query_run.assert_called_once_with(
        "test-cloud-account",
        as_admin=True,
        from_projects=["project1", "project2"],
        all_projects=False,
    )

    server_query_append_from = server_query_run.return_value.append_from
    server_query_append_from.assert_called_once_with(
        "PROJECT_QUERY", "test-cloud-account", ProjectProperties.PROJECT_NAME
    )

    server_query_select = server_query_append_from.return_value.select
    server_query_select.assert_called_once_with(
        ServerProperties.SERVER_ID,
        ServerProperties.SERVER_NAME,
        ServerProperties.ADDRESSES,
    )

    server_query_then = server_query_select.return_value.then
    server_query_then.assert_called_once_with("USER_QUERY", keep_previous_results=True)

    user_query_run = server_query_then.return_value.run
    user_query_run.assert_called_once_with("test-cloud-account")

    user_query_select = user_query_run.return_value.select
    user_query_select.assert_called_once_with(UserProperties.USER_NAME)

    user_query_group_by = user_query_select.return_value.group_by
    user_query_group_by.assert_called_once_with(UserProperties.USER_EMAIL)

    assert res == user_query_group_by.return_value


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


@patch("workflows.email.send_decom_flavor_email.EmailTemplateDetails")
@patch("workflows.email.send_decom_flavor_email.EmailParams")
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
                template_name="decom_email",
                template_params={
                    "username": user_name,
                    "affected_flavors": flavor_table,
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


@pytest.fixture(name="run_send_decom_flavor_email_test_case")
def run_send_decom_flavor_email_test_case_fixture():
    # pylint: disable=too-many-arguments
    @patch("workflows.email.send_decom_flavor_email.validate")
    @patch("workflows.email.send_decom_flavor_email.find_users_with_decom_flavors")
    @patch("workflows.email.send_decom_flavor_email.build_email_params")
    @patch("workflows.email.send_decom_flavor_email.print_email_params")
    @patch("workflows.email.send_decom_flavor_email.Emailer")
    def _run_send_decom_flavor_email_test_case(
        mock_emailer,
        mock_print_email,
        mock_build_email,
        mock_find_users,
        mock_validate,
        use_override=False,
        cc_cloud_support=False,
        send_email=False,
    ):
        override_email_address = "override-email@example.com"
        flavor_name_list = ["flavor1", "flavor2"]
        limit_by_projects = NonCallableMock()
        all_projects = NonCallableMock()
        cloud_account = NonCallableMock()
        as_html = NonCallableMock()
        smtp_account = NonCallableMock()
        email_param_kwargs = {"arg1": "val1", "arg2": "val2"}

        mock_find_users.return_value.to_props.return_value = {
            "user_email1": [
                {
                    "user_name": "user1",
                    # doesn't matter what else we find since we use to_string()
                },
            ],
            "user_email2": [{"user_name": "user2"}],
        }

        send_decom_flavor_email(
            smtp_account=smtp_account,
            cloud_account=cloud_account,
            flavor_name_list=flavor_name_list,
            limit_by_projects=limit_by_projects,
            all_projects=all_projects,
            as_html=as_html,
            send_email=send_email,
            override_email_address=override_email_address,
            cc_cloud_support=cc_cloud_support,
            **email_param_kwargs,
        )

        mock_validate.assert_called_once_with(
            flavor_name_list, limit_by_projects, all_projects
        )

        mock_find_users.assert_called_once_with(
            cloud_account, flavor_name_list, limit_by_projects
        )

        exp_email_to = ("user_email1", "user_email2")
        exp_email_cc = None

        if use_override:
            exp_email_to = (override_email_address, override_email_address)

        if cc_cloud_support:
            exp_email_cc = ("cloud-support@stfc.ac.uk",)

        if send_email:
            mock_build_email.assert_has_calls(
                [
                    call(
                        "user1",
                        "flavor1, flavor2",
                        mock_find_users.return_value.to_string.return_value,
                        email_to=exp_email_to[0],
                        as_html=as_html,
                        email_cc=exp_email_cc,
                        **email_param_kwargs,
                    ),
                    call(
                        "user2",
                        "flavor1, flavor2",
                        mock_find_users.return_value.to_string.return_value,
                        email_to=exp_email_to[1],
                        as_html=as_html,
                        email_cc=exp_email_cc,
                        **email_param_kwargs,
                    ),
                ]
            )

            mock_emailer.assert_has_calls(
                [
                    call(smtp_account),
                    call().send_emails([mock_build_email.return_value]),
                    call(smtp_account),
                    call().send_emails([mock_build_email.return_value]),
                ]
            )
        else:
            mock_print_email.assert_has_calls(
                [
                    call(
                        exp_email_to[0],
                        "user1",
                        as_html,
                        "flavor1, flavor2",
                        mock_find_users.return_value.to_string.return_value,
                    ),
                    call(
                        exp_email_to[1],
                        "user2",
                        as_html,
                        "flavor1, flavor2",
                        mock_find_users.return_value.to_string.return_value,
                    ),
                ]
            )

            mock_find_users.return_value.to_string.assert_has_calls(
                [call(groups=["user_email1"]), call(groups=["user_email2"])]
            )

    return _run_send_decom_flavor_email_test_case


def test_send_decom_flavor_email_print_params(run_send_decom_flavor_email_test_case):
    """
    Tests that send_decom_flavor_email() function prints params when send_email set to false
    """
    run_send_decom_flavor_email_test_case(
        use_override=False,
        send_email=False,
    )

    # with override email set
    run_send_decom_flavor_email_test_case(use_override=True, send_email=False)


def test_send_decom_flavor_email(run_send_decom_flavor_email_test_case):
    """
    Tests that send_decom_flavor_email() function sends email with valid params
    """
    run_send_decom_flavor_email_test_case(
        use_override=None, cc_cloud_support=False, send_email=True
    )

    # with override email set and cc_cloud_support
    run_send_decom_flavor_email_test_case(
        use_override=True,
        cc_cloud_support=True,
        send_email=True,
    )


@patch("workflows.email.send_decom_flavor_email.validate")
@patch("workflows.email.send_decom_flavor_email.find_users_with_decom_flavors")
@patch("workflows.email.send_decom_flavor_email.build_email_params")
@patch("workflows.email.send_decom_flavor_email.Emailer")
def test_send_decom_flavor_email_send_plaintext(
    mock_emailer, mock_build_email_params, mock_find_users, mock_validate
):
    """
    Tests send_decom_flavor() function actually sends email - as_html false
    """

    flavor_name_list = ["flavor1", "flavor2"]
    limit_by_projects = NonCallableMock()
    all_projects = NonCallableMock()
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_query = mock_find_users.return_value
    mock_query.to_props.return_value = {
        "user_email1": [
            {
                "user_name": "user1",
                # doesn't matter what else we find since we use to_string()
            },
        ],
        "user_email2": [{"user_name": "user2"}],
    }

    send_decom_flavor_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        flavor_name_list=flavor_name_list,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=False,
        send_email=True,
        use_override=False,
        **mock_kwargs,
    )

    mock_validate.assert_called_once_with(
        flavor_name_list, limit_by_projects, all_projects
    )
    mock_find_users.assert_called_once_with(
        cloud_account, flavor_name_list, limit_by_projects
    )
    mock_query.to_props.assert_called_once()

    mock_build_email_params.assert_has_calls(
        [
            call(
                "user1",
                "flavor1, flavor2",
                mock_query.to_string.return_value,
                email_to=["user_email1"],
                as_html=False,
                email_cc=None,
                **mock_kwargs,
            ),
            call(
                "user2",
                "flavor1, flavor2",
                mock_query.to_string.return_value,
                email_to=["user_email2"],
                as_html=False,
                email_cc=None,
                **mock_kwargs,
            ),
        ]
    )

    mock_query.to_string.assert_has_calls(
        [call(groups=["user_email1"]), call(groups=["user_email2"])]
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )


@patch("workflows.email.send_decom_flavor_email.validate")
@patch("workflows.email.send_decom_flavor_email.find_users_with_decom_flavors")
@patch("workflows.email.send_decom_flavor_email.build_email_params")
@patch("workflows.email.send_decom_flavor_email.get_flavor_list_html")
@patch("workflows.email.send_decom_flavor_email.Emailer")
def test_send_decom_flavor_email_send_html(
    mock_emailer,
    mock_get_flavor_list_html,
    mock_build_email_params,
    mock_find_users,
    mock_validate,
):
    """
    Tests send_decom_flavor() function actually sends email - as_html True
    """

    flavor_name_list = ["flavor1", "flavor2"]
    limit_by_projects = NonCallableMock()
    all_projects = NonCallableMock()
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_query = mock_find_users.return_value
    mock_query.to_props.return_value = {
        "user_email1": [
            {
                "user_name": "user1",
                # doesn't matter what else we find since we use to_string()
            },
        ],
        "user_email2": [{"user_name": "user2"}],
    }

    send_decom_flavor_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        flavor_name_list=flavor_name_list,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=True,
        send_email=True,
        use_override=False,
        **mock_kwargs,
    )

    mock_validate.assert_called_once_with(
        flavor_name_list, limit_by_projects, all_projects
    )
    mock_find_users.assert_called_once_with(
        cloud_account, flavor_name_list, limit_by_projects
    )
    mock_query.to_props.assert_called_once()

    mock_build_email_params.assert_has_calls(
        [
            call(
                "user1",
                mock_get_flavor_list_html.return_value,
                mock_query.to_html.return_value,
                email_to=["user_email1"],
                as_html=True,
                email_cc=None,
                **mock_kwargs,
            ),
            call(
                "user2",
                mock_get_flavor_list_html.return_value,
                mock_query.to_html.return_value,
                email_to=["user_email2"],
                as_html=True,
                email_cc=None,
                **mock_kwargs,
            ),
        ]
    )

    mock_get_flavor_list_html.assert_has_calls(
        [call(["flavor1", "flavor2"]), call(["flavor1", "flavor2"])]
    )

    mock_query.to_html.assert_has_calls(
        [call(groups=["user_email1"]), call(groups=["user_email2"])]
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )


@patch("workflows.email.send_decom_flavor_email.validate")
@patch("workflows.email.send_decom_flavor_email.find_users_with_decom_flavors")
@patch("workflows.email.send_decom_flavor_email.print_email_params")
def test_send_decom_flavor_email_print(
    mock_print_email_params, mock_find_users, mock_validate
):
    """
    Tests send_decom_flavor() function prints when send_email=False
    """

    flavor_name_list = ["flavor1", "flavor2"]
    limit_by_projects = NonCallableMock()
    all_projects = NonCallableMock()
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_query = mock_find_users.return_value
    mock_query.to_props.return_value = {
        "user_email1": [
            {
                "user_name": "user1",
                # doesn't matter what else we find since we use to_string()
            },
        ],
        "user_email2": [{"user_name": "user2"}],
    }

    send_decom_flavor_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        flavor_name_list=flavor_name_list,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=True,
        send_email=False,
        use_override=False,
        **mock_kwargs,
    )

    mock_validate.assert_called_once_with(
        flavor_name_list, limit_by_projects, all_projects
    )
    mock_find_users.assert_called_once_with(
        cloud_account, flavor_name_list, limit_by_projects
    )
    mock_query.to_props.assert_called_once()

    mock_print_email_params.assert_has_calls(
        [
            call(
                "user_email1",
                "user1",
                True,
                "flavor1, flavor2",
                mock_query.to_string.return_value,
            ),
            call(
                "user_email2",
                "user2",
                True,
                "flavor1, flavor2",
                mock_query.to_string.return_value,
            ),
        ]
    )

    mock_query.to_string.assert_has_calls(
        [call(groups=["user_email1"]), call(groups=["user_email2"])]
    )


@patch("workflows.email.send_decom_flavor_email.validate")
@patch("workflows.email.send_decom_flavor_email.find_users_with_decom_flavors")
@patch("workflows.email.send_decom_flavor_email.build_email_params")
@patch("workflows.email.send_decom_flavor_email.Emailer")
def test_send_decom_flavor_email_use_override(
    mock_emailer, mock_build_email_params, mock_find_users, mock_validate
):
    """
    Tests send_decom_flavor() function sends email to override email - when use_override set
    """

    flavor_name_list = ["flavor1", "flavor2"]
    limit_by_projects = NonCallableMock()
    all_projects = NonCallableMock()
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_query = mock_find_users.return_value
    mock_query.to_props.return_value = {
        "user_email1": [
            {
                "user_name": "user1",
                # doesn't matter what else we find since we use to_string()
            },
        ],
        "user_email2": [{"user_name": "user2"}],
    }
    override_email_address = "example@stfc.ac.uk"

    send_decom_flavor_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        flavor_name_list=flavor_name_list,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=False,
        send_email=True,
        use_override=True,
        override_email_address=override_email_address,
        **mock_kwargs,
    )

    mock_validate.assert_called_once_with(
        flavor_name_list, limit_by_projects, all_projects
    )
    mock_find_users.assert_called_once_with(
        cloud_account, flavor_name_list, limit_by_projects
    )
    mock_query.to_props.assert_called_once()

    mock_build_email_params.assert_has_calls(
        [
            call(
                "user1",
                "flavor1, flavor2",
                mock_query.to_string.return_value,
                email_to=[override_email_address],
                as_html=False,
                email_cc=None,
                **mock_kwargs,
            ),
            call(
                "user2",
                "flavor1, flavor2",
                mock_query.to_string.return_value,
                email_to=[override_email_address],
                as_html=False,
                email_cc=None,
                **mock_kwargs,
            ),
        ]
    )

    mock_query.to_string.assert_has_calls(
        [call(groups=["user_email1"]), call(groups=["user_email2"])]
    )

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )


@patch("workflows.email.send_decom_flavor_email.validate")
@patch("workflows.email.send_decom_flavor_email.find_users_with_decom_flavors")
@patch("workflows.email.send_decom_flavor_email.build_email_params")
@patch("workflows.email.send_decom_flavor_email.Emailer")
def test_send_decom_flavor_email_when_result_email_none(
    mock_emailer, mock_build_email_params, mock_find_users, mock_validate
):
    """
    Tests send_decom_flavor() function sends to override email - when email set to None
    """

    flavor_name_list = ["flavor1", "flavor2"]
    limit_by_projects = NonCallableMock()
    all_projects = NonCallableMock()
    cloud_account = NonCallableMock()
    smtp_account = NonCallableMock()
    mock_kwargs = {"arg1": "val1", "arg2": "val2"}

    mock_query = mock_find_users.return_value
    mock_query.to_props.return_value = {
        None: [
            {
                "user_name": "user1",
                # doesn't matter what else we find since we use to_string()
            },
        ],
    }
    override_email_address = "example@stfc.ac.uk"

    send_decom_flavor_email(
        smtp_account=smtp_account,
        cloud_account=cloud_account,
        flavor_name_list=flavor_name_list,
        limit_by_projects=limit_by_projects,
        all_projects=all_projects,
        as_html=False,
        send_email=True,
        use_override=False,
        override_email_address=override_email_address,
        **mock_kwargs,
    )

    mock_validate.assert_called_once_with(
        flavor_name_list, limit_by_projects, all_projects
    )
    mock_find_users.assert_called_once_with(
        cloud_account, flavor_name_list, limit_by_projects
    )
    mock_query.to_props.assert_called_once()

    mock_build_email_params.assert_called_once_with(
        "user1",
        "flavor1, flavor2",
        mock_query.to_string.return_value,
        email_to=[override_email_address],
        as_html=False,
        email_cc=None,
        **mock_kwargs,
    )

    mock_query.to_string.assert_called_once_with(groups=[None])

    mock_emailer.assert_has_calls(
        [
            call(smtp_account),
            call().send_emails([mock_build_email_params.return_value]),
        ]
    )
