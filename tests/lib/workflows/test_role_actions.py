from unittest.mock import patch, MagicMock

from enums.user_domains import UserDomains
from structs.role_details import RoleDetails
from workflows.role_actions import role_add, role_remove, role_assign_group


@patch("workflows.role_actions.openstack_roles.assign_role_to_user")
def test_role_add(mock_api_assign_role_to_user):
    """
    Tests that role_add function forwards on request to openstack API role_add function
    and returns the correct status (True)
    """

    # setup input values
    mock_conn = MagicMock()
    mock_user_identifier = "user-id"
    mock_project_identifier = "project-id"
    mock_role_identifier = "user"
    mock_user_domain = "stfc"

    status = role_add(
        mock_conn,
        mock_user_identifier,
        mock_project_identifier,
        mock_role_identifier,
        mock_user_domain,
    )

    mock_api_assign_role_to_user.assert_called_once_with(
        mock_conn,
        details=RoleDetails(
            user_identifier=mock_user_identifier,
            project_identifier=mock_project_identifier,
            role_identifier=mock_role_identifier,
            user_domain=UserDomains.STFC,
        ),
    )

    assert status


@patch("workflows.role_actions.assign_group_role_to_project")
def test_role_assign_group(mock_api_assign_group_role_to_project):
    """
    Tests that role_add function forwards on request to openstack API role_add function
    and returns the correct status (True)
    """

    # setup input values
    mock_conn = MagicMock()
    mock_project_identifier = "project-id"
    mock_role_identifier = "user"
    mock_group_name = "group-name"

    status = role_assign_group(
        mock_conn,
        mock_project_identifier,
        mock_role_identifier,
        mock_group_name,
    )

    mock_api_assign_group_role_to_project.assert_called_once_with(
        mock_conn,
        project=mock_project_identifier,
        role=mock_role_identifier,
        group=mock_group_name,
    )

    assert status


@patch("workflows.role_actions.openstack_roles.remove_role_from_user")
def test_role_remove(mock_api_remove_role_from_user):
    """
    Tests that role_add function forwards on request to openstack API role_add function
    and returns the correct status (True)
    """

    # setup input values
    mock_conn = MagicMock()
    mock_user_identifier = "user-id"
    mock_project_identifier = "project-id"
    mock_role_identifier = "user"
    mock_user_domain = "stfc"

    status = role_remove(
        mock_conn,
        mock_user_identifier,
        mock_project_identifier,
        mock_role_identifier,
        mock_user_domain,
    )

    mock_api_remove_role_from_user.assert_called_once_with(
        mock_conn,
        details=RoleDetails(
            user_identifier=mock_user_identifier,
            project_identifier=mock_project_identifier,
            role_identifier=mock_role_identifier,
            user_domain=UserDomains.STFC,
        ),
    )

    assert status
