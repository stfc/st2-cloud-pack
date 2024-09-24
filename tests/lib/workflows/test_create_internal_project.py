from unittest.mock import patch, MagicMock

from enums.rbac_network_actions import RbacNetworkActions
from enums.user_domains import UserDomains

from structs.network_rbac import NetworkRbac
from structs.project_details import ProjectDetails
from structs.role_details import RoleDetails

from workflows.create_internal_project import create_internal_project


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
@patch("workflows.create_internal_project.create_project")
@patch("workflows.create_internal_project.refresh_security_groups")
@patch("workflows.create_internal_project.create_internal_security_group_rules")
@patch("workflows.create_internal_project.create_http_security_group")
@patch("workflows.create_internal_project.create_https_security_group")
@patch("workflows.create_internal_project.create_network_rbac")
@patch("workflows.create_internal_project.assign_role_to_user")
def test_create_internal_project(
    mock_assign_role_to_user,
    mock_create_network_rbac,
    mock_create_https_security_group,
    mock_create_http_security_group,
    mock_create_internal_security_group_rules,
    mock_refresh_security_groups,
    mock_create_project,
):
    # Mock the return value of create_project
    mock_create_project.return_value = {"id": "project-id"}

    # Test data
    mock_conn = MagicMock()
    project_name = "Test Project"
    project_email = "test@example.com"
    project_description = "Test Description"
    project_immutable = True
    parent_id = "parent-id"
    admin_user_list = ["admin1", "admin2"]
    stfc_user_list = ["user1", "user2"]

    # Call the function
    create_internal_project(
        mock_conn,
        project_name,
        project_email,
        project_description,
        project_immutable,
        parent_id,
        admin_user_list,
        stfc_user_list,
    )

    mock_create_project.assert_called_once_with(
        mock_conn,
        ProjectDetails(
            name=project_name,
            email=project_email,
            description=project_description,
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )
    mock_refresh_security_groups.assert_called_once_with(mock_conn, "project-id")
    mock_create_internal_security_group_rules.assert_called_once_with(
        mock_conn, "project-id", "default"
    )
    mock_create_http_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )
    mock_create_https_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )
    mock_create_network_rbac.assert_called_once_with(
        mock_conn,
        NetworkRbac(
            project_identifier="project-id",
            network_identifier="Internal",
            action=RbacNetworkActions.SHARED,
        ),
    )

    # Assert that roles were assigned to the admins
    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="admin1",
            user_domain=UserDomains.DEFAULT,
            project_identifier="project-id",
            role_identifier="admin",
        ),
    )
    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="admin2",
            user_domain=UserDomains.DEFAULT,
            project_identifier="project-id",
            role_identifier="admin",
        ),
    )

    # Assert that roles were assigned to the stfc users
    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user1",
            user_domain=UserDomains.STFC,
            project_identifier="project-id",
            role_identifier="user",
        ),
    )
    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user2",
            user_domain=UserDomains.STFC,
            project_identifier="project-id",
            role_identifier="user",
        ),
    )

    # Verify assign_role_to_user was called four times
    # (two for admin, two for stfc users)
    assert mock_assign_role_to_user.call_count == 4
