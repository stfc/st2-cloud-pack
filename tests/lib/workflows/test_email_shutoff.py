from unittest.mock import NonCallableMock, patch

from nose.tools import raises

from enums.query.props.server_properties import ServerProperties
from enums.query.props.user_properties import UserProperties
from enums.query.query_presets import QueryPresetsGeneric
from structs.email.email_params import EmailParams
from workflows.email_shutoff import send_user_email, query_shutoff_vms, query_user_details, main, extract_user_details


def test_send_user_email():
    """
    Test that an email is sent with the send_email method
    """
    mock_email = NonCallableMock()
    mock_subject = NonCallableMock()
    with patch('workflows.email_shutoff.Emailer') as mock_emailer:
        send_user_email(mock_email, mock_subject)

    mock_emailer.assert_called_once()
    email_object = mock_emailer.return_value

    mock_email_params = EmailParams(
        subject=mock_subject,
        email_from='cloud-support@stfc.ac.uk',
        email_to=mock_email,
        email_templates=[]
    )

    email_object.send_emails.assert_called_once_with([mock_email_params])


def test_query_shutoff_vms_no_project_id():
    """
    Test that we can query machines that are in shutoff (stopped)
    state
    Testing the case where no project id is given (query all projects)
    """
    mock_project_id = None

    with patch('workflows.email_shutoff.ServerQuery') as mock_server_query:
        res = query_shutoff_vms(mock_project_id)

    server_object = mock_server_query.return_value
    server_object.select.assert_called_once_with(ServerProperties.SERVER_NAME)

    select_object = server_object.select.return_value
    select_object.where.assert_called_once_with(QueryPresetsGeneric.EQUAL_TO, ServerProperties.SERVER_STATUS,value="STOPPED")

    where_object = select_object.where.return_value
    where_object.group_by.assert_called_once_with(ServerProperties.USER_ID)

    server_object.run.assert_called_once_with("openstack")
    server_object.to_list.assert_called_once()

    assert res == server_object.to_list.return_value


def test_query_shutoff_vms_project_id():
    """
    Test that we can query machines that are in shutoff (stopped) state
    Tests the case where a project id has been given
    """

    mock_project_id = NonCallableMock()

    with patch('workflows.email_shutoff.ServerQuery') as mock_server_query:
        query_shutoff_vms(mock_project_id)

    server_object = mock_server_query.return_value

    server_object.run.assert_called_once_with("openstack", from_projects=mock_project_id)


def test_query_user_details():
    """
    Test that we query to get username and email from user id
    """
    mock_user_id = NonCallableMock()

    with patch('workflows.email_shutoff.UserQuery') as mock_user_query:
        res = query_user_details(mock_user_id)

    user_object = mock_user_query.return_value
    user_object.select.assert_called_once_with(UserProperties.USER_NAME, UserProperties.USER_EMAIL)

    select_object = user_object.select.return_value
    select_object.where.assert_called_once_with(QueryPresetsGeneric.EQUAL_TO, UserProperties.USER_ID, value=mock_user_id)

    user_object.run.assert_called_once_with("openstack")
    user_object.to_list.assert_called_once()

    assert res == user_object.to_list.return_value


def test_extract_user_details():
    mock_user_list = [NonCallableMock()]
    mock_user_name = NonCallableMock()
    mock_user_email = NonCallableMock()
    mock_return_value = [{'user_name': mock_user_name,
                         'user_email': mock_user_email}]

    with patch('workflows.email_shutoff.query_user_details') as mock_query_user:
        mock_query_user.return_value = mock_return_value
        names, emails = extract_user_details(mock_user_list)

    assert names[mock_user_list[0]] == mock_user_name
    assert emails[mock_user_list[0]] == mock_user_email

# TODO - Add test to check KeyError is raised when a user has no email address


@raises(KeyError)
def test_extract_user_details_no_email():
    """
    Test that KeyError is raised if a user has no email address
    """
    # patch extract_user_details method?
    # when method called, mock query_user_detail.return_value

    # mock query_user_details method returning a value for user detail
    # mock user_detail dictionary where user_detail['user_email'] is None

    # assert extract_user_details raises a KeyError?


# TODO - Add test for main method


def test_main():
    """
    Test that we can query for a shutoff machine,
    get the user_id and query to get details, then send email
    """

    pass