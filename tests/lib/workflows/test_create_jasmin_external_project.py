from unittest.mock import patch, MagicMock

from enums.network_providers import NetworkProviders
from enums.rbac_network_actions import RbacNetworkActions
from enums.user_domains import UserDomains
from structs.network_details import NetworkDetails
from structs.network_rbac import NetworkRbac
from structs.project_details import ProjectDetails
from structs.quota_details import QuotaDetails
from structs.role_details import RoleDetails
from structs.router_details import RouterDetails
from workflows.create_jasmin_external_project import create_jasmin_external_project


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
@patch("workflows.create_jasmin_external_project.create_project")
@patch("workflows.create_jasmin_external_project.create_network")
@patch("workflows.create_jasmin_external_project.create_router")
@patch("workflows.create_jasmin_external_project.create_subnet")
@patch("workflows.create_jasmin_external_project.add_interface_to_router")
@patch("workflows.create_jasmin_external_project.refresh_security_groups")
@patch("workflows.create_jasmin_external_project.set_quota")
@patch("workflows.create_jasmin_external_project.create_external_security_group_rules")
@patch("workflows.create_jasmin_external_project.create_http_security_group")
@patch("workflows.create_jasmin_external_project.create_https_security_group")
@patch("workflows.create_jasmin_external_project.create_network_rbac")
@patch("workflows.create_jasmin_external_project.allocate_floating_ips")
@patch("workflows.create_jasmin_external_project.assign_role_to_user")
def test_create_jasmin_external_project(
    mock_assign_role_to_user,
    mock_allocate_floating_ips,
    mock_create_network_rbac,
    mock_create_https_security_group,
    mock_create_http_security_group,
    mock_create_external_security_group_rules,
    mock_set_quota,
    mock_refresh_security_groups,
    mock_add_interface_to_router,
    mock_create_subnet,
    mock_create_router,
    mock_create_network,
    mock_create_project,
):
    """
    Tests the workflow for creating a JASMIN project with external networking
    """
    # Mock the return values for project, network, router, and subnet
    mock_create_project.return_value = {"id": "project-id"}
    mock_create_network.return_value = {"id": "network-id"}
    mock_create_router.return_value = {"id": "router-id"}
    mock_create_subnet.return_value = {"id": "subnet-id"}

    # Test data
    mock_conn = MagicMock()
    project_name = "Test Project"
    project_email = "test@example.com"
    domain = "test-domain"
    project_description = "Test Description"
    network_name = "External Network"
    subnet_name = "External Subnet"
    router_name = "External Router"
    number_of_floating_ips = 2
    number_of_security_group_rules = 200
    project_immutable = True
    parent_id = "parent-id"
    admin_user_list = ["admin1", "admin2"]
    jasmin_user_list = ["user1", "user2"]

    # Call the function
    create_jasmin_external_project(
        mock_conn,
        project_name,
        project_email,
        domain,
        project_description,
        network_name,
        subnet_name,
        router_name,
        number_of_floating_ips,
        number_of_security_group_rules,
        project_immutable,
        parent_id,
        admin_user_list,
        jasmin_user_list,
    )

    # Assertions to ensure the functions were called with correct parameters
    mock_create_project.assert_called_once_with(
        mock_conn,
        ProjectDetails(
            name=project_name,
            email=project_email,
            domain=domain,
            description=project_description,
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )

    mock_create_network.assert_called_once_with(
        mock_conn,
        NetworkDetails(
            name=network_name,
            description="",
            project_identifier="project-id",
            provider_network_type=NetworkProviders.VXLAN,
            port_security_enabled=True,
            has_external_router=False,
        ),
    )

    mock_create_router.assert_called_once_with(
        mock_conn,
        RouterDetails(
            router_name=router_name,
            router_description="",
            project_identifier="project-id",
            external_gateway="External",
            is_distributed=False,
        ),
    )
    mock_create_subnet.assert_called_once_with(
        mock_conn,
        network_identifier="network-id",
        subnet_name=subnet_name,
        subnet_description="",
        dhcp_enabled=True,
    )
    mock_add_interface_to_router.assert_called_once_with(
        mock_conn,
        project_identifier="project-id",
        router_identifier="router-id",
        subnet_identifier="subnet-id",
    )
    mock_refresh_security_groups.assert_called_once_with(mock_conn, "project-id")

    mock_set_quota.assert_called_once_with(
        mock_conn,
        QuotaDetails(
            project_identifier="project-id",
            num_floating_ips=number_of_floating_ips,
            num_security_group_rules=number_of_security_group_rules,
        ),
    )

    mock_create_external_security_group_rules.assert_called_once_with(
        mock_conn, project_identifier="project-id", security_group_identifier="default"
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
            network_identifier="network-id",
            action=RbacNetworkActions.SHARED,
        ),
    )
    mock_allocate_floating_ips.assert_called_once_with(
        mock_conn,
        network_identifier="External",
        project_identifier="project-id",
        number_to_create=number_of_floating_ips,
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

    # Assert that roles were assigned to the jasmin users
    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user1",
            user_domain=UserDomains.JASMIN,
            project_identifier="project-id",
            role_identifier="user",
        ),
    )
    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user2",
            user_domain=UserDomains.JASMIN,
            project_identifier="project-id",
            role_identifier="user",
        ),
    )

    # Verify assign_role_to_user was called four times
    # (two for admin, two for jasmin users)
    assert mock_assign_role_to_user.call_count == 4


@patch("workflows.create_jasmin_external_project.create_project")
@patch("workflows.create_jasmin_external_project.create_network")
@patch("workflows.create_jasmin_external_project.create_router")
@patch("workflows.create_jasmin_external_project.create_subnet")
@patch("workflows.create_jasmin_external_project.add_interface_to_router")
@patch("workflows.create_jasmin_external_project.refresh_security_groups")
@patch("workflows.create_jasmin_external_project.set_quota")
@patch("workflows.create_jasmin_external_project.create_external_security_group_rules")
@patch("workflows.create_jasmin_external_project.create_http_security_group")
@patch("workflows.create_jasmin_external_project.create_https_security_group")
@patch("workflows.create_jasmin_external_project.create_network_rbac")
@patch("workflows.create_jasmin_external_project.allocate_floating_ips")
@patch("workflows.create_jasmin_external_project.assign_role_to_user")
def test_create_jasmin_external_project_no_admin_users(
    mock_assign_role_to_user,
    mock_allocate_floating_ips,
    mock_create_network_rbac,
    mock_create_https_security_group,
    mock_create_http_security_group,
    mock_create_external_security_group_rules,
    mock_set_quota,
    mock_refresh_security_groups,
    mock_add_interface_to_router,
    mock_create_subnet,
    mock_create_router,
    mock_create_network,
    mock_create_project,
):
    """
    Tests the workflow for creating a JASMIN project with external networking
    with no admin usernames included
    """
    # Mock the return values for project, network, router, and subnet
    mock_create_project.return_value = {"id": "project-id"}
    mock_create_network.return_value = {"id": "network-id"}
    mock_create_router.return_value = {"id": "router-id"}
    mock_create_subnet.return_value = {"id": "subnet-id"}

    # Test data
    mock_conn = MagicMock()
    project_name = "Test Project"
    project_email = "test@example.com"
    domain = "test-domain"
    project_description = "Test Description"
    network_name = "External Network"
    subnet_name = "External Subnet"
    router_name = "External Router"
    number_of_floating_ips = 2
    number_of_security_group_rules = 200
    project_immutable = True
    parent_id = "parent-id"
    admin_user_list = None
    jasmin_user_list = ["user1", "user2"]

    # Call the function
    create_jasmin_external_project(
        mock_conn,
        project_name,
        project_email,
        domain,
        project_description,
        network_name,
        subnet_name,
        router_name,
        number_of_floating_ips,
        number_of_security_group_rules,
        project_immutable,
        parent_id,
        admin_user_list,
        jasmin_user_list,
    )

    # Assertions to ensure the functions were called with correct parameters
    mock_create_project.assert_called_once_with(
        mock_conn,
        ProjectDetails(
            name=project_name,
            email=project_email,
            domain=domain,
            description=project_description,
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )

    mock_create_network.assert_called_once_with(
        mock_conn,
        NetworkDetails(
            name=network_name,
            description="",
            project_identifier="project-id",
            provider_network_type=NetworkProviders.VXLAN,
            port_security_enabled=True,
            has_external_router=False,
        ),
    )

    mock_create_router.assert_called_once_with(
        mock_conn,
        RouterDetails(
            router_name=router_name,
            router_description="",
            project_identifier="project-id",
            external_gateway="External",
            is_distributed=False,
        ),
    )
    mock_create_subnet.assert_called_once_with(
        mock_conn,
        network_identifier="network-id",
        subnet_name=subnet_name,
        subnet_description="",
        dhcp_enabled=True,
    )
    mock_add_interface_to_router.assert_called_once_with(
        mock_conn,
        project_identifier="project-id",
        router_identifier="router-id",
        subnet_identifier="subnet-id",
    )
    mock_refresh_security_groups.assert_called_once_with(mock_conn, "project-id")

    mock_set_quota.assert_called_once_with(
        mock_conn,
        QuotaDetails(
            project_identifier="project-id",
            num_floating_ips=number_of_floating_ips,
            num_security_group_rules=number_of_security_group_rules,
        ),
    )

    mock_create_external_security_group_rules.assert_called_once_with(
        mock_conn, project_identifier="project-id", security_group_identifier="default"
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
            network_identifier="network-id",
            action=RbacNetworkActions.SHARED,
        ),
    )
    mock_allocate_floating_ips.assert_called_once_with(
        mock_conn,
        network_identifier="External",
        project_identifier="project-id",
        number_to_create=number_of_floating_ips,
    )

    # Assert that roles were assigned to the jasmin users
    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user1",
            user_domain=UserDomains.JASMIN,
            project_identifier="project-id",
            role_identifier="user",
        ),
    )
    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user2",
            user_domain=UserDomains.JASMIN,
            project_identifier="project-id",
            role_identifier="user",
        ),
    )

    # Verify assign_role_to_user was called two times
    # (zero for admin, two for jasmin users)
    assert mock_assign_role_to_user.call_count == 2
