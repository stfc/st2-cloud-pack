from unittest.mock import MagicMock, patch

import pytest
from parameterized import parameterized


from enums.network_providers import NetworkProviders
from enums.rbac_network_actions import RbacNetworkActions
from enums.user_domains import UserDomains
from structs.network_details import NetworkDetails
from structs.network_rbac import NetworkRbac
from structs.project_details import ProjectDetails
from structs.quota_details import QuotaDetails
from structs.role_details import RoleDetails
from structs.router_details import RouterDetails
from workflows.create_project import (
    create_project,
    validate_jasmin_args,
    setup_external_networking,
    setup_internal_networking,
)


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
@patch("workflows.create_project.create_openstack_project")
@patch("workflows.create_project.refresh_security_groups")
@patch("workflows.create_project.setup_external_networking")
@patch("workflows.create_project.create_http_security_group")
@patch("workflows.create_project.create_https_security_group")
@patch("workflows.create_project.set_quota")
@patch("workflows.create_project.allocate_floating_ips")
@patch("workflows.create_project.assign_role_to_user")
def test_create_project_external(
    mock_assign_role_to_user,
    mock_allocate_floating_ips,
    mock_set_quota,
    mock_create_https_security_group,
    mock_create_http_security_group,
    mock_setup_external_networking,
    mock_refresh_security_groups,
    mock_create_openstack_project,
):
    # Mock the return value for project
    mock_project = MagicMock()
    mock_project.name = "Test Project"
    mock_project.__getitem__.side_effect = lambda key: {"id": "project-id"}[key]
    mock_create_openstack_project.return_value = mock_project

    # Test data
    mock_conn = MagicMock()
    project_name = "Test Project"
    project_email = "test@example.com"
    project_description = "Test Description"
    project_domain = "default"
    user_domain = "stfc"
    network = "External"
    number_of_floating_ips = 2
    number_of_security_group_rules = 200
    project_immutable = True
    parent_id = "parent-id"
    admin_user_list = ["admin1", "admin2"]
    user_list = ["user1", "user2"]

    # Call the function
    create_project(
        mock_conn,
        project_name,
        project_email,
        project_description,
        project_domain,
        user_domain,
        network,
        number_of_floating_ips,
        number_of_security_group_rules,
        project_immutable,
        parent_id,
        admin_user_list,
        user_list,
    )

    # Assertions to ensure the functions were called with correct parameters
    mock_create_openstack_project.assert_called_once_with(
        mock_conn,
        ProjectDetails(
            name=project_name,
            email=project_email,
            description=project_description,
            project_domain=project_domain,
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )

    mock_refresh_security_groups.assert_called_once_with(mock_conn, "project-id")

    mock_setup_external_networking.assert_called_once_with(
        mock_conn, mock_project, network
    )

    mock_create_http_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    mock_create_https_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    mock_set_quota.assert_called_once_with(
        mock_conn,
        QuotaDetails(
            project_identifier="project-id",
            num_floating_ips=number_of_floating_ips,
            num_security_group_rules=number_of_security_group_rules,
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

    # Assert that roles were assigned to the stfc users
    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user1",
            user_domain="stfc",
            project_identifier="project-id",
            role_identifier="user",
        ),
    )

    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user2",
            user_domain="stfc",
            project_identifier="project-id",
            role_identifier="user",
        ),
    )

    # Verify assign_role_to_user was called four times
    # (two for admin, two for stfc users)
    assert mock_assign_role_to_user.call_count == 4


@patch("workflows.create_project.create_openstack_project")
@patch("workflows.create_project.refresh_security_groups")
@patch("workflows.create_project.setup_internal_networking")
@patch("workflows.create_project.create_http_security_group")
@patch("workflows.create_project.create_https_security_group")
@patch("workflows.create_project.set_quota")
@patch("workflows.create_project.allocate_floating_ips")
@patch("workflows.create_project.assign_role_to_user")
def test_create_project_internal(
    mock_assign_role_to_user,
    mock_allocate_floating_ips,
    mock_set_quota,
    mock_create_https_security_group,
    mock_create_http_security_group,
    mock_setup_internal_networking,
    mock_refresh_security_groups,
    mock_create_openstack_project,
):
    # Mock the return value for project
    mock_project = MagicMock()
    mock_project.name = "Test Project"
    mock_project.__getitem__.side_effect = lambda key: {"id": "project-id"}[key]
    mock_create_openstack_project.return_value = mock_project

    # Test data
    mock_conn = MagicMock()
    project_name = "Test Project"
    project_email = "test@example.com"
    project_description = "Test Description"
    project_domain = "default"
    user_domain = "stfc"
    network = "Internal"
    number_of_floating_ips = 2
    number_of_security_group_rules = 200
    project_immutable = True
    parent_id = "parent-id"
    admin_user_list = ["admin1", "admin2"]
    user_list = ["user1", "user2"]

    # Call the function
    create_project(
        mock_conn,
        project_name,
        project_email,
        project_description,
        project_domain,
        user_domain,
        network,
        number_of_floating_ips,
        number_of_security_group_rules,
        project_immutable,
        parent_id,
        admin_user_list,
        user_list,
    )

    # Assertions to ensure the functions were called with correct parameters
    mock_create_openstack_project.assert_called_once_with(
        mock_conn,
        ProjectDetails(
            name=project_name,
            email=project_email,
            description=project_description,
            project_domain=project_domain,
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )

    mock_refresh_security_groups.assert_called_once_with(mock_conn, "project-id")

    mock_setup_internal_networking.assert_called_once_with(mock_conn, mock_project)

    mock_create_http_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    mock_create_https_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    mock_set_quota.assert_called_once_with(
        mock_conn,
        QuotaDetails(
            project_identifier="project-id",
            num_floating_ips=number_of_floating_ips,
            num_security_group_rules=number_of_security_group_rules,
        ),
    )

    mock_allocate_floating_ips.assert_called_once_with(
        mock_conn,
        network_identifier="Internal",
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

    # Assert that roles were assigned to the stfc users
    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user1",
            user_domain="stfc",
            project_identifier="project-id",
            role_identifier="user",
        ),
    )

    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user2",
            user_domain="stfc",
            project_identifier="project-id",
            role_identifier="user",
        ),
    )

    # Verify assign_role_to_user was called four times
    # (two for admin, two for stfc users)
    assert mock_assign_role_to_user.call_count == 4


@patch("workflows.create_project.create_openstack_project")
@patch("workflows.create_project.refresh_security_groups")
@patch("workflows.create_project.setup_external_networking")
@patch("workflows.create_project.create_http_security_group")
@patch("workflows.create_project.create_https_security_group")
@patch("workflows.create_project.set_quota")
@patch("workflows.create_project.allocate_floating_ips")
@patch("workflows.create_project.assign_role_to_user")
def test_create_project_jasmin(
    mock_assign_role_to_user,
    mock_allocate_floating_ips,
    mock_set_quota,
    mock_create_https_security_group,
    mock_create_http_security_group,
    mock_setup_external_networking,
    mock_refresh_security_groups,
    mock_create_openstack_project,
):
    # Mock the return value for project
    mock_project = MagicMock()
    mock_project.name = "Test Project"
    mock_project.__getitem__.side_effect = lambda key: {"id": "project-id"}[key]
    mock_create_openstack_project.return_value = mock_project

    # Test data
    mock_conn = MagicMock()
    project_name = "Test Project"
    project_email = "test@example.com"
    project_description = "Test Description"
    project_domain = "jasmin"
    user_domain = "jasmin"
    network = "JASMIN External Cloud Network"
    number_of_floating_ips = 2
    number_of_security_group_rules = 200
    project_immutable = True
    parent_id = "parent-id"
    admin_user_list = ["admin1", "admin2"]
    user_list = ["user1", "user2"]

    # Call the function
    create_project(
        mock_conn,
        project_name,
        project_email,
        project_description,
        project_domain,
        user_domain,
        network,
        number_of_floating_ips,
        number_of_security_group_rules,
        project_immutable,
        parent_id,
        admin_user_list,
        user_list,
    )

    # Assertions to ensure the functions were called with correct parameters
    mock_create_openstack_project.assert_called_once_with(
        mock_conn,
        ProjectDetails(
            name=project_name,
            email=project_email,
            description=project_description,
            project_domain=project_domain,
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )

    mock_refresh_security_groups.assert_called_once_with(mock_conn, "project-id")

    mock_setup_external_networking.assert_called_once_with(
        mock_conn, mock_project, network
    )

    mock_create_http_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    mock_create_https_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    mock_set_quota.assert_called_once_with(
        mock_conn,
        QuotaDetails(
            project_identifier="project-id",
            num_floating_ips=number_of_floating_ips,
            num_security_group_rules=number_of_security_group_rules,
        ),
    )

    mock_allocate_floating_ips.assert_called_once_with(
        mock_conn,
        network_identifier="JASMIN External Cloud Network",
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

    # Assert that roles were assigned to the stfc users
    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user1",
            user_domain="jasmin",
            project_identifier="project-id",
            role_identifier="user",
        ),
    )

    mock_assign_role_to_user.assert_any_call(
        mock_conn,
        RoleDetails(
            user_identifier="user2",
            user_domain="jasmin",
            project_identifier="project-id",
            role_identifier="user",
        ),
    )

    # Verify assign_role_to_user was called four times
    # (two for admin, two for stfc users)
    assert mock_assign_role_to_user.call_count == 4


@patch("workflows.create_project.create_openstack_project")
@patch("workflows.create_project.refresh_security_groups")
@patch("workflows.create_project.setup_external_networking")
@patch("workflows.create_project.create_http_security_group")
@patch("workflows.create_project.create_https_security_group")
@patch("workflows.create_project.set_quota")
@patch("workflows.create_project.allocate_floating_ips")
@patch("workflows.create_project.assign_role_to_user")
def test_create_project_jasmin_no_users(
    mock_assign_role_to_user,
    mock_allocate_floating_ips,
    mock_set_quota,
    mock_create_https_security_group,
    mock_create_http_security_group,
    mock_setup_external_networking,
    mock_refresh_security_groups,
    mock_create_openstack_project,
):
    # Mock the return value for project
    mock_project = MagicMock()
    mock_project.name = "Test Project"
    mock_project.__getitem__.side_effect = lambda key: {"id": "project-id"}[key]
    mock_create_openstack_project.return_value = mock_project

    # Test data
    mock_conn = MagicMock()
    project_name = "Test Project"
    project_email = "test@example.com"
    project_description = "Test Description"
    project_domain = "jasmin"
    user_domain = "jasmin"
    network = "JASMIN External Cloud Network"
    number_of_floating_ips = 2
    number_of_security_group_rules = 200
    project_immutable = True
    parent_id = "parent-id"
    admin_user_list = None
    user_list = None

    # Call the function
    create_project(
        mock_conn,
        project_name,
        project_email,
        project_description,
        project_domain,
        user_domain,
        network,
        number_of_floating_ips,
        number_of_security_group_rules,
        project_immutable,
        parent_id,
        admin_user_list,
        user_list,
    )

    # Assertions to ensure the functions were called with correct parameters
    mock_create_openstack_project.assert_called_once_with(
        mock_conn,
        ProjectDetails(
            name=project_name,
            email=project_email,
            description=project_description,
            project_domain=project_domain,
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )

    mock_refresh_security_groups.assert_called_once_with(mock_conn, "project-id")

    mock_setup_external_networking.assert_called_once_with(
        mock_conn, mock_project, network
    )

    mock_create_http_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    mock_create_https_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    mock_set_quota.assert_called_once_with(
        mock_conn,
        QuotaDetails(
            project_identifier="project-id",
            num_floating_ips=number_of_floating_ips,
            num_security_group_rules=number_of_security_group_rules,
        ),
    )

    mock_allocate_floating_ips.assert_called_once_with(
        mock_conn,
        network_identifier="JASMIN External Cloud Network",
        project_identifier="project-id",
        number_to_create=number_of_floating_ips,
    )

    # Verify assign_role_to_user was called 0 times
    assert mock_assign_role_to_user.call_count == 0


@parameterized.expand(
    [
        (
            "invalid_project_domain",
            {
                "project_domain": "stfc",
                "user_domain": "jasmin",
                "network": "JASMIN External Cloud Network",
            },
        ),
        (
            "invalid_user_domain",
            {
                "project_domain": "jasmin",
                "user_domain": "default",
                "network": "JASMIN External Cloud Network",
            },
        ),
        (
            "invalid_network",
            {
                "project_domain": "jasmin",
                "user_domain": "jasmin",
                "network": "Internal",
            },
        ),
    ]
)
def test_create_project_invalid_jasmin_args(_, args):
    # Test data
    mock_conn = MagicMock()
    project_name = "JASMIN Project"
    project_email = "JASMIN@example.com"
    project_description = "Test Description"
    project_domain = args["project_domain"]
    user_domain = args["user_domain"]
    network = args["network"]
    number_of_floating_ips = 2
    number_of_security_group_rules = 200
    project_immutable = True
    parent_id = "parent-id"
    admin_user_list = ["admin1", "admin2"]
    user_list = ["user1", "user2"]

    # Call the function
    with pytest.raises(ValueError):
        create_project(
            mock_conn,
            project_name,
            project_email,
            project_description,
            project_domain,
            user_domain,
            network,
            number_of_floating_ips,
            number_of_security_group_rules,
            project_immutable,
            parent_id,
            admin_user_list,
            user_list,
        )


@parameterized.expand(
    [
        (
            "invalid_project_domain",
            {
                "project_domain": "stfc",
                "user_domain": "jasmin",
                "network": "JASMIN External Cloud Network",
            },
        ),
        (
            "invalid_user_domain",
            {
                "project_domain": "jasmin",
                "user_domain": "default",
                "network": "JASMIN External Cloud Network",
            },
        ),
        (
            "invalid_network",
            {
                "project_domain": "jasmin",
                "user_domain": "jasmin",
                "network": "Internal",
            },
        ),
    ]
)
def test_validate_jasmin_args(_, args):
    # Call the function
    with pytest.raises(ValueError):
        validate_jasmin_args(
            args["project_domain"], args["user_domain"], args["network"]
        )


@patch("workflows.create_project.create_network")
@patch("workflows.create_project.create_router")
@patch("workflows.create_project.create_subnet")
@patch("workflows.create_project.add_interface_to_router")
@patch("workflows.create_project.create_network_rbac")
@patch("workflows.create_project.create_external_security_group_rules")
def test_setup_external_networking(
    mock_create_external_security_group_rules,
    mock_create_network_rbac,
    mock_add_interface_to_router,
    mock_create_subnet,
    mock_create_router,
    mock_create_network,
):
    # Mock the return values for network, router, and subnet
    mock_create_network.return_value = {"id": "network-id"}
    mock_create_router.return_value = {"id": "router-id"}
    mock_create_subnet.return_value = {"id": "subnet-id"}

    # Test data
    mock_conn = MagicMock()
    mock_project = MagicMock()
    mock_project.name = "Test Project"
    mock_project.__getitem__.side_effect = lambda key: {"id": "project-id"}[key]
    network = "External"

    # Call the function
    setup_external_networking(mock_conn, mock_project, network)

    # Assertions to ensure the functions were called with correct parameters
    mock_create_network.assert_called_once_with(
        mock_conn,
        NetworkDetails(
            name="Test Project-network",
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
            router_name="Test Project-router",
            router_description="",
            project_identifier="project-id",
            external_gateway="External",
            is_distributed=False,
        ),
    )
    mock_create_subnet.assert_called_once_with(
        mock_conn,
        network_identifier="network-id",
        subnet_name="Test Project-subnet",
        subnet_description="",
        dhcp_enabled=True,
    )
    mock_add_interface_to_router.assert_called_once_with(
        mock_conn,
        project_identifier="project-id",
        router_identifier="router-id",
        subnet_identifier="subnet-id",
    )

    mock_create_network_rbac.assert_called_once_with(
        mock_conn,
        NetworkRbac(
            project_identifier="project-id",
            network_identifier="network-id",
            action=RbacNetworkActions.SHARED,
        ),
    )

    mock_create_external_security_group_rules.assert_called_once_with(
        mock_conn, project_identifier="project-id", security_group_identifier="default"
    )


@patch("workflows.create_project.create_network_rbac")
@patch("workflows.create_project.create_internal_security_group_rules")
def test_setup_internal_networking(
    mock_create_internal_security_group_rules,
    mock_create_network_rbac,
):
    # Test data
    mock_conn = MagicMock()
    mock_project = MagicMock()
    mock_project.name = "Test Project"
    mock_project.__getitem__.side_effect = lambda key: {"id": "project-id"}[key]

    # Call the function
    setup_internal_networking(mock_conn, mock_project)

    # Assertions to ensure the functions were called with correct parameters
    mock_create_network_rbac.assert_called_once_with(
        mock_conn,
        NetworkRbac(
            project_identifier="project-id",
            network_identifier="Internal",
            action=RbacNetworkActions.SHARED,
        ),
    )

    mock_create_internal_security_group_rules.assert_called_once_with(
        mock_conn, "project-id", "default"
    )


def test_project_create_raise_unknown_network_type():
    """
    Test project creation with unknown network type
    """
    mock_conn = MagicMock()
    mock_project = "mock_project"
    mock_email = "email@example.com"
    mock_description = "mock_description"
    mock_domain = "default"
    mock_user_domain = "stfc"
    mock_network = "not_a_network"

    with pytest.raises(NotImplementedError):
        create_project(
            mock_conn,
            mock_project,
            mock_email,
            mock_description,
            mock_domain,
            mock_user_domain,
            mock_network,
        )
