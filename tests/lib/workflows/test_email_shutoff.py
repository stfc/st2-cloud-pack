from unittest.mock import NonCallableMock, patch, call
from enums.query.props.server_properties import ServerProperties
from enums.query.props.user_properties import UserProperties
from enums.query.query_presets import QueryPresetsGeneric, QueryPresetsDateTime
from structs.email.email_params import EmailParams
from workflows.email_shutoff import (
    send_user_email,
    query_shutoff_vms,
    main,
    prepare_user_server_email,
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

    with patch("workflows.email_shutoff.ServerQuery") as mock_server_query:
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

    with patch("workflows.email_shutoff.ServerQuery") as mock_server_query:
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

    with patch("workflows.email_shutoff.ServerQuery") as mock_server_query:
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


def test_prepare_user_server_email():
    """
    Tests that we extract the user_email and names of servers
    from the server_query_result parameter
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

    expected_email = fake_server_a["user_email"]
    expected_server_names = [fake_server_a["server_name"], fake_server_b["server_name"]]

    result_email, result_server_names = prepare_user_server_email(fake_query_result)

    assert result_email == expected_email
    assert result_server_names == expected_server_names


def test_send_user_email():
    """
    Test that an email is sent with the send_email method
    """
    mock_smtp_account = NonCallableMock()
    mock_email_from = NonCallableMock()
    mock_user_email = NonCallableMock()
    mock_server_list = NonCallableMock()

    with patch("workflows.email_shutoff.Emailer") as mock_emailer:
        send_user_email(
            mock_smtp_account, mock_email_from, mock_user_email, mock_server_list
        )

    mock_emailer.assert_called_once()
    email_object = mock_emailer.return_value

    expected_email_params = EmailParams(
        subject=f"VM Shutoff {mock_server_list}",
        email_from=mock_email_from,
        email_to=[mock_user_email],
        email_templates=[],
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
    with patch("workflows.email_shutoff.Emailer") as mock_emailer:
        send_user_email(
            mock_smtp_account, mock_email_from, mock_user_email, mock_server_list
        )

    expected_email_params = EmailParams(
        subject=f"VM Shutoff {mock_server_list}",
        email_from=mock_email_from,
        email_to=["cloud-support@stfc.ac.uk"],
        email_templates=[],
    )

    mock_emailer.assert_called_once()
    email_object = mock_emailer.return_value

    email_object.send_emails.assert_called_once_with([expected_email_params])


@patch("workflows.email_shutoff.query_shutoff_vms")
@patch("workflows.email_shutoff.prepare_user_server_email")
@patch("workflows.email_shutoff.send_user_email")
def test_main(send_user_email, prepare_user_server_email, query_shutoff_vms):
    """
    Test that we can query for a shutoff machine,
    get the user_id and query to get details, then send email
    """

    mock_smtp_account = NonCallableMock()
    mock_cloud_account = NonCallableMock()
    mock_email_from = NonCallableMock()
    mock_project_id = NonCallableMock()
    mock_days_threshold = NonCallableMock()

    mock_data = {
        "a": [{"server_name": NonCallableMock(), "user_email": NonCallableMock()}],
        "b": [{"server_name": NonCallableMock(), "user_email": NonCallableMock()}],
    }

    mocked_user_a = (NonCallableMock(), NonCallableMock())
    mocked_user_b = (NonCallableMock(), NonCallableMock())

    prepare_user_server_email.side_effect = [mocked_user_a, mocked_user_b]
    query_shutoff_vms.return_value = mock_data

    main(
        mock_smtp_account,
        mock_cloud_account,
        mock_email_from,
        mock_project_id,
        mock_days_threshold,
    )

    query_shutoff_vms.assert_called_once_with(
        mock_cloud_account, mock_project_id, mock_days_threshold
    )

    assert prepare_user_server_email.call_count == 2

    prepare_user_server_email.assert_has_calls(
        [call(mock_data["a"]), call(mock_data["b"])]
    )

    assert send_user_email.call_count == 2

    expected_email_user_a = call(
        mock_smtp_account, mock_email_from, mocked_user_a[0], mocked_user_a[1]
    )
    expected_email_user_b = call(
        mock_smtp_account, mock_email_from, mocked_user_b[0], mocked_user_b[1]
    )
    expected_email_args = [expected_email_user_a, expected_email_user_b]
    send_user_email.assert_has_calls(expected_email_args)
