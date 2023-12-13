from unittest.mock import NonCallableMock, patch, call
from enums.query.props.server_properties import ServerProperties
from enums.query.props.user_properties import UserProperties
from enums.query.query_presets import QueryPresetsGeneric, QueryPresetsDateTime
from structs.email.email_params import EmailParams
from workflows.send_shutoff_server_email import (
    send_user_email,
    query_shutoff_vms,
    find_user_info,
    extract_server_list,
    UserDetails,
    send_shutoff_server_email,
)


def test_query_shutoff_vms_no_project_id():
    """
    Test that we can query machines that are in shutoff (stopped)
    state
    Testing the case where no project id is given (query all projects)
    """
    mock_cloud_account = NonCallableMock()
    mock_project_id = None
    mock_days_threshold = NonCallableMock()

    with patch("workflows.send_shutoff_server_email.ServerQuery") as mock_server_query:
        query_shutoff_vms(mock_cloud_account, mock_project_id, mock_days_threshold)

    server_object = mock_server_query.return_value
    server_object.select.assert_called_once_with(ServerProperties.SERVER_NAME)

    select_object = server_object.select.return_value

    select_object.where.assert_called_once_with(
        QueryPresetsGeneric.EQUAL_TO, ServerProperties.SERVER_STATUS, value="SHUTOFF"
    )

    where_status_object = select_object.where.return_value

    where_status_object.where.assert_called_once_with(
        QueryPresetsDateTime.OLDER_THAN,
        ServerProperties.SERVER_LAST_UPDATED_DATE,
        days=mock_days_threshold,
    )

    server_object.run.assert_called_once_with(
        mock_cloud_account, as_admin=True, all_projects=True
    )


def test_query_shutoff_vms_project_id():
    """
    Test that we can query machines that are in shutoff (stopped) state
    Tests the case where a project id has been given
    """
    mock_cloud_account = NonCallableMock()
    mock_project_id = NonCallableMock()

    with patch("workflows.send_shutoff_server_email.ServerQuery") as mock_server_query:
        query_shutoff_vms(mock_cloud_account, mock_project_id)

    server_object = mock_server_query.return_value

    server_object.run.assert_called_once_with(
        mock_cloud_account, as_admin=True, from_projects=mock_project_id
    )

    user_query = server_object.then.return_value

    user_query.run.assert_called_once_with(mock_cloud_account)


def test_query_server_get_user_details():
    """
    Tests that we get the details of the user from a server query
    This tests the user query section of the query chaining used in the method
    """
    mock_cloud_account = NonCallableMock()
    mock_project_id = None

    with patch("workflows.send_shutoff_server_email.ServerQuery") as mock_server_query:
        res = query_shutoff_vms(mock_cloud_account, mock_project_id)

    server_object = mock_server_query.return_value
    server_object.then.assert_called_once_with("USER_QUERY", keep_previous_results=True)

    user_query = server_object.then.return_value
    user_query.select.assert_called_once_with(UserProperties.USER_EMAIL)
    select_object = user_query.select.return_value

    select_object.group_by.assert_called_once_with(UserProperties.USER_NAME)

    user_query.run.assert_called_once_with(mock_cloud_account)

    user_query.to_props.assert_called_once()

    assert res == user_query.to_props.return_value


@patch("workflows.send_shutoff_server_email.UserQuery")
def test_find_user_info_with_email(mock_user_query):
    """
    Test that we can run a user query to get the user name and
    user email using a user id.
    This is the case where a user has an email address.
    """

    mock_cloud_account = NonCallableMock()
    mock_user_id = "test01"
    mock_override_email = NonCallableMock()

    mock_user_query.return_value.to_props.return_value = {
        "user_name": ["test_user"],
        "user_email": ["test_user@example.com"],
    }

    res = find_user_info(mock_user_id, mock_cloud_account, mock_override_email)

    user_object = mock_user_query.return_value
    user_object.select.assert_called_once_with(
        UserProperties.USER_NAME, UserProperties.USER_EMAIL
    )

    select_object = user_object.select.return_value

    select_object.where.assert_called_once_with(
        QueryPresetsGeneric.EQUAL_TO, UserProperties.USER_ID, value=mock_user_id
    )

    user_object.run.assert_called_once_with(cloud_account=mock_cloud_account)

    user_object.to_props.assert_called_once_with(flatten=True)

    assert res.name == "test_user"
    assert res.email == "test_user@example.com"


@patch("workflows.send_shutoff_server_email.UserQuery")
def test_find_user_info_not_valid(mock_user_query):
    """
    Test that we can run a user query and return expected values for when
    a query is not valid
    """

    mock_cloud_acount = NonCallableMock()
    mock_user_id = NonCallableMock()
    mock_override_email = NonCallableMock()

    mock_user_query.return_value.to_props.return_value = None

    res = find_user_info(mock_user_id, mock_cloud_acount, mock_override_email)

    assert res.name == ""
    assert res.email == mock_override_email


def test_extract_server_list():
    """
    Tests that we extract a list of server names from the server_query_result parameter
    """
    fake_server_a = {
        "server_name": NonCallableMock(),
        "user_email": "example@example.com",
    }
    fake_server_b = {
        "server_name": NonCallableMock(),
        "user_email": "example@example.com",
    }

    fake_query_result = [fake_server_a, fake_server_b]

    expected_server_names = [fake_server_a["server_name"], fake_server_b["server_name"]]

    result_server_names = extract_server_list(fake_query_result)

    assert result_server_names == expected_server_names


def test_send_user_email():
    """
    Test that an email is sent with the send_email method
    """
    mock_smtp_account = NonCallableMock()
    mock_email_from = NonCallableMock()
    mock_user_email = NonCallableMock()
    mock_server_list = NonCallableMock()
    mock_cc_email = True
    mock_email_template = NonCallableMock()

    with patch("workflows.send_shutoff_server_email.Emailer") as mock_emailer:
        send_user_email(
            mock_smtp_account,
            mock_email_from,
            mock_user_email,
            mock_cc_email,
            mock_server_list,
            mock_email_template,
        )

    mock_emailer.assert_called_once()
    email_object = mock_emailer.return_value

    expected_email_params = EmailParams(
        subject=f"VM Shutoff {mock_server_list}",
        email_from=mock_email_from,
        email_to=[mock_user_email],
        email_cc=("cloud-support@stfc.ac.uk",),
        email_templates=[mock_email_template],
    )

    email_object.send_emails.assert_called_once_with([expected_email_params])


def test_send_user_email_no_email_given():
    """
    Tests that if no email address was associated with a user, then
    the Cloud Support email address is used by default.
    """
    mock_smtp_account = NonCallableMock()
    mock_email_from = NonCallableMock()
    mock_user_email = None
    mock_server_list = NonCallableMock()
    mock_email_template = NonCallableMock()
    mock_email_cc = True
    with patch("workflows.send_shutoff_server_email.Emailer") as mock_emailer:
        send_user_email(
            mock_smtp_account,
            mock_email_from,
            mock_user_email,
            mock_email_cc,
            mock_server_list,
            mock_email_template,
        )

    expected_email_params = EmailParams(
        subject=f"VM Shutoff {mock_server_list}",
        email_from=mock_email_from,
        email_to=["cloud-support@stfc.ac.uk"],
        email_cc=("cloud-support@stfc.ac.uk",),
        email_templates=[mock_email_template],
    )
    mock_emailer.assert_called_once()
    email_object = mock_emailer.return_value
    email_object.send_emails.assert_called_once_with([expected_email_params])


@patch("workflows.send_shutoff_server_email.query_shutoff_vms")
@patch("workflows.send_shutoff_server_email.find_user_info")
@patch("workflows.send_shutoff_server_email.extract_server_list")
@patch("workflows.send_shutoff_server_email.send_user_email")
def test_send_shutoff_server_email(
    mock_send_user_email,
    mock_extract_server_list,
    mock_find_user_info,
    mock_query_shutoff,
):
    """
    Test that we can query for shutoff VMs, get user info and list of servers to build and send
    an email
    """

    # pylint: disable=too-many-locals

    mock_smtp_account = NonCallableMock()
    mock_cloud_account = NonCallableMock()
    mock_email_from = NonCallableMock()
    mock_override_email_address = NonCallableMock()
    mock_limit_by_project = NonCallableMock()
    mock_days_threshold = NonCallableMock()
    mock_email_template = NonCallableMock()
    mock_email_cc = True
    mock_send_email = True

    # mock username and email for each user
    mocked_user_a = UserDetails(id="user_id_a", name="a", email="a@example.com")
    mocked_user_b = UserDetails(id="user_id_b", name="b", email="b@example.com")
    mock_find_user_info.side_effect = [mocked_user_a, mocked_user_b]

    # mock list of servers
    mocked_user_a_servers = [NonCallableMock(), NonCallableMock()]
    mocked_user_b_servers = [NonCallableMock(), NonCallableMock()]
    mock_extract_server_list.side_effect = [
        mocked_user_a_servers,
        mocked_user_b_servers,
    ]

    mock_data = {
        "user_id_a": [
            {"user_email": NonCallableMock(), "server_name": NonCallableMock()}
        ],
        "user_id_b": [
            {"user_email": NonCallableMock(), "server_name": NonCallableMock()}
        ],
    }
    mock_query_shutoff.return_value = mock_data

    send_shutoff_server_email(
        mock_smtp_account,
        mock_cloud_account,
        mock_email_from,
        mock_override_email_address,
        mock_limit_by_project,
        mock_days_threshold,
        mock_email_template,
        mock_email_cc,
        mock_send_email,
    )

    mock_query_shutoff.assert_called_once_with(
        mock_cloud_account, mock_limit_by_project, mock_days_threshold
    )

    assert mock_find_user_info.call_count == 2
    mock_find_user_info.assert_has_calls(
        [
            call(
                mock_data["user_id_a"], mock_cloud_account, mock_override_email_address
            ),
            call(
                mock_data["user_id_b"], mock_cloud_account, mock_override_email_address
            ),
        ],
    )

    assert mock_extract_server_list.call_count == 2
    mock_extract_server_list.assert_has_calls(
        [call(mock_data["user_id_a"]), call(mock_data["user_id_b"])]
    )

    assert mock_send_user_email.call_count == 2

    mock_send_user_email.assert_has_calls(
        [
            call(
                mock_smtp_account,
                mock_email_from,
                mocked_user_a.email,
                mock_email_cc,
                mocked_user_a_servers,
                mock_email_template,
            ),
            call(
                mock_smtp_account,
                mock_email_from,
                mocked_user_b.email,
                mock_email_cc,
                mocked_user_b_servers,
                mock_email_template,
            ),
        ]
    )
