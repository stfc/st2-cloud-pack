import logging
from unittest.mock import MagicMock, NonCallableMock, call, patch

import pytest

from apis.openstack_api.enums.network_providers import NetworkProviders
from apis.openstack_api.enums.networks import Networks
from apis.openstack_api.enums.rbac_network_actions import RbacNetworkActions
from apis.openstack_api.enums.user_domains import UserDomains
from apis.openstack_api.structs.network_details import NetworkDetails
from apis.openstack_api.structs.network_rbac import NetworkRbac
from apis.openstack_api.structs.project_details import ProjectDetails
from apis.openstack_api.structs.quota_details import QuotaDetails
from apis.openstack_api.structs.role_details import RoleDetails
from apis.openstack_api.structs.router_details import RouterDetails
from workflows.create_project import (
    create_project,
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
@patch("workflows.create_project.assign_role_to_user")
def test_create_project_external(
    mock_assign_role_to_user,
    mock_create_https_security_group,
    mock_create_http_security_group,
    mock_setup_external_networking,
    mock_refresh_security_groups,
    mock_create_openstack_project,
):
    """
    Test the creation of an external OpenStack project.
    """
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
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )

    mock_refresh_security_groups.assert_called_once_with(mock_conn, "project-id")

    mock_setup_external_networking.assert_called_once_with(
        mock_conn,
        mock_project,
        Networks.EXTERNAL,
        number_of_floating_ips,
        number_of_security_group_rules,
    )

    mock_create_http_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    mock_create_https_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
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


@patch("workflows.create_project.create_openstack_project")
@patch("workflows.create_project.refresh_security_groups")
@patch("workflows.create_project.setup_internal_networking")
@patch("workflows.create_project.create_http_security_group")
@patch("workflows.create_project.create_https_security_group")
@patch("workflows.create_project.assign_role_to_user")
def test_create_project_internal(
    mock_assign_role_to_user,
    mock_create_https_security_group,
    mock_create_http_security_group,
    mock_setup_internal_networking,
    mock_refresh_security_groups,
    mock_create_openstack_project,
):
    """
    Test the creation of an internal OpenStack project.
    """
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


@patch("workflows.create_project.create_openstack_project")
@patch("workflows.create_project.refresh_security_groups")
@patch("workflows.create_project.setup_external_networking")
@patch("workflows.create_project.create_http_security_group")
@patch("workflows.create_project.create_https_security_group")
@patch("workflows.create_project.assign_role_to_user")
def test_create_project_jasmin(
    mock_assign_role_to_user,
    mock_create_https_security_group,
    mock_create_http_security_group,
    mock_setup_external_networking,
    mock_refresh_security_groups,
    mock_create_openstack_project,
):
    """
    Test the creation of a JASMIN external OpenStack project.
    """
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
    user_domain = "jasmin"
    network = "Jasmin"
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
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )

    mock_refresh_security_groups.assert_called_once_with(mock_conn, "project-id")

    mock_setup_external_networking.assert_called_once_with(
        mock_conn,
        mock_project,
        Networks.JASMIN,
        number_of_floating_ips,
        number_of_security_group_rules,
    )

    mock_create_http_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    mock_create_https_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
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
    # (two for admin, two for stfc users)
    assert mock_assign_role_to_user.call_count == 4


@patch("workflows.create_project.create_openstack_project")
@patch("workflows.create_project.refresh_security_groups")
@patch("workflows.create_project.setup_external_networking")
@patch("workflows.create_project.create_http_security_group")
@patch("workflows.create_project.create_https_security_group")
@patch("workflows.create_project.assign_role_to_user")
def test_create_project_jasmin_no_users(
    mock_assign_role_to_user,
    mock_create_https_security_group,
    mock_create_http_security_group,
    mock_setup_external_networking,
    mock_refresh_security_groups,
    mock_create_openstack_project,
):
    """
    Test the creation of a JASMIN OpenStack project without inputting user lists.
    """
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
    user_domain = "jasmin"
    network = "Jasmin"
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
            immutable=project_immutable,
            parent_id=parent_id,
            is_enabled=True,
        ),
    )

    mock_refresh_security_groups.assert_called_once_with(mock_conn, "project-id")

    mock_setup_external_networking.assert_called_once_with(
        mock_conn,
        mock_project,
        Networks.JASMIN,
        number_of_floating_ips,
        number_of_security_group_rules,
    )

    mock_create_http_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    mock_create_https_security_group.assert_called_once_with(
        mock_conn, project_identifier="project-id"
    )

    # Verify assign_role_to_user was called 0 times
    assert mock_assign_role_to_user.call_count == 0


@patch("workflows.create_project.create_network")
@patch("workflows.create_project.create_router")
@patch("workflows.create_project.create_subnet")
@patch("workflows.create_project.add_interface_to_router")
@patch("workflows.create_project.set_quota")
@patch("workflows.create_project.create_network_rbac")
@patch("workflows.create_project.create_external_security_group_rules")
@patch("workflows.create_project.allocate_floating_ips")
def test_setup_external_networking(
    mock_allocate_floating_ips,
    mock_create_external_security_group_rules,
    mock_create_network_rbac,
    mock_set_quota,
    mock_add_interface_to_router,
    mock_create_subnet,
    mock_create_router,
    mock_create_network,
):
    """
    Test the setup of networking for external projects.
    """
    logging.disable()  # Don't need to test logging
    # Mock the return values for network, router, and subnet
    mock_create_network.return_value = MagicMock()
    mock_create_router.return_value = MagicMock()
    mock_create_subnet.return_value = MagicMock()

    # Test data
    mock_conn = MagicMock()
    mock_project = MagicMock()
    mock_project.name = "Test Project"
    mock_network = "External"
    number_of_floating_ips = 2
    number_of_security_group_rules = 200

    # Call the function
    setup_external_networking(
        mock_conn,
        mock_project,
        Networks.EXTERNAL,
        number_of_floating_ips,
        number_of_security_group_rules,
    )

    # Assertions to ensure the functions were called with correct parameters
    mock_create_network.assert_called_once_with(
        mock_conn,
        NetworkDetails(
            name="Test Project-network",
            description="",
            project_identifier=mock_project.id,
            provider_network_type=NetworkProviders.VXLAN,
            port_security_enabled=True,
            has_external_router=False,
        ),
    )

    mock_create_network_rbac.assert_has_calls(
        [
            call(
                mock_conn,
                NetworkRbac(
                    project_identifier=mock_project.id,
                    network_identifier="External",
                    action=RbacNetworkActions.EXTERNAL,
                ),
            ),
            call(
                mock_conn,
                NetworkRbac(
                    project_identifier=mock_project.id,
                    network_identifier=mock_create_network.return_value.id,
                    action=RbacNetworkActions.SHARED,
                ),
            ),
        ]
    )

    mock_create_router.assert_called_once_with(
        mock_conn,
        RouterDetails(
            router_name=f"{mock_project.name}-router",
            router_description="",
            project_identifier=mock_project.id,
            external_gateway=mock_network,
            is_distributed=False,
        ),
    )

    mock_create_subnet.assert_called_once_with(
        mock_conn,
        network_identifier=mock_create_network.return_value.id,
        subnet_name=f"{mock_project.name}-subnet",
        subnet_description="",
        dhcp_enabled=True,
    )

    mock_add_interface_to_router.assert_called_once_with(
        mock_conn,
        project_identifier=mock_project.id,
        router_identifier=mock_create_router.return_value.id,
        subnet_identifier=mock_create_subnet.return_value.id,
    )

    mock_set_quota.assert_called_once_with(
        mock_conn,
        QuotaDetails(
            project_identifier=mock_project.id,
            floating_ips=number_of_floating_ips,
            security_group_rules=number_of_security_group_rules,
        ),
    )

    mock_create_external_security_group_rules.assert_called_once_with(
        mock_conn,
        project_identifier=mock_project.id,
        security_group_identifier="default",
    )

    mock_allocate_floating_ips.assert_called_once_with(
        mock_conn,
        network_identifier="External",
        project_identifier=mock_project.id,
        number_to_create=number_of_floating_ips,
    )


@patch("workflows.create_project.create_network")
@patch("workflows.create_project.create_router")
@patch("workflows.create_project.create_subnet")
@patch("workflows.create_project.add_interface_to_router")
@patch("workflows.create_project.set_quota")
@patch("workflows.create_project.create_network_rbac")
@patch("workflows.create_project.create_jasmin_security_group_rules")
@patch("workflows.create_project.allocate_floating_ips")
def test_setup_jasmin_networking(
    mock_allocate_floating_ips,
    mock_create_jasmin_security_group_rules,
    mock_create_network_rbac,
    mock_set_quota,
    mock_add_interface_to_router,
    mock_create_subnet,
    mock_create_router,
    mock_create_network,
):
    """
    Test the setup of networking for external projects.
    """
    logging.disable()  # Don't need to test logging
    # Mock the return values for network, router, and subnet
    mock_create_network.return_value = MagicMock()
    mock_create_router.return_value = MagicMock()
    mock_create_subnet.return_value = MagicMock()

    # Test data
    mock_conn = MagicMock()
    mock_project = MagicMock()
    mock_project.name = "Test Project"
    number_of_floating_ips = 2
    number_of_security_group_rules = 200

    # Call the function
    setup_external_networking(
        mock_conn,
        mock_project,
        Networks.JASMIN,
        number_of_floating_ips,
        number_of_security_group_rules,
    )

    # Assertions to ensure the functions were called with correct parameters
    mock_create_network.assert_called_once_with(
        mock_conn,
        NetworkDetails(
            name="Test Project-network",
            description="",
            project_identifier=mock_project.id,
            provider_network_type=NetworkProviders.VXLAN,
            port_security_enabled=True,
            has_external_router=False,
        ),
    )

    mock_create_network_rbac.assert_has_calls(
        [
            call(
                mock_conn,
                NetworkRbac(
                    project_identifier=mock_project.id,
                    network_identifier="JASMIN External Cloud Network",
                    action=RbacNetworkActions.EXTERNAL,
                ),
            ),
            call(
                mock_conn,
                NetworkRbac(
                    project_identifier=mock_project.id,
                    network_identifier=mock_create_network.return_value.id,
                    action=RbacNetworkActions.SHARED,
                ),
            ),
        ]
    )

    mock_create_router.assert_called_once_with(
        mock_conn,
        RouterDetails(
            router_name=f"{mock_project.name}-router",
            router_description="",
            project_identifier=mock_project.id,
            external_gateway="JASMIN External Cloud Network",
            is_distributed=False,
        ),
    )

    mock_create_subnet.assert_called_once_with(
        mock_conn,
        network_identifier=mock_create_network.return_value.id,
        subnet_name=f"{mock_project.name}-subnet",
        subnet_description="",
        dhcp_enabled=True,
    )

    mock_add_interface_to_router.assert_called_once_with(
        mock_conn,
        project_identifier=mock_project.id,
        router_identifier=mock_create_router.return_value.id,
        subnet_identifier=mock_create_subnet.return_value.id,
    )

    mock_set_quota.assert_called_once_with(
        mock_conn,
        QuotaDetails(
            project_identifier=mock_project.id,
            floating_ips=number_of_floating_ips,
            security_group_rules=number_of_security_group_rules,
        ),
    )

    mock_create_jasmin_security_group_rules.assert_called_once_with(
        mock_conn,
        project_identifier=mock_project.id,
        security_group_identifier="default",
    )

    mock_allocate_floating_ips.assert_called_once_with(
        mock_conn,
        network_identifier="JASMIN External Cloud Network",
        project_identifier=mock_project.id,
        number_to_create=number_of_floating_ips,
    )


@patch("workflows.create_project.create_network_rbac")
@patch("workflows.create_project.create_internal_security_group_rules")
def test_setup_internal_networking(
    mock_create_internal_security_group_rules,
    mock_create_network_rbac,
):
    """
    Test the setup of networking for internal projects.
    """
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
    Test project creation with an unknown network type.
    """
    mock_conn = MagicMock()
    mock_project = "mock_project"
    mock_email = "email@example.com"
    mock_description = "mock_description"
    mock_user_domain = "stfc"
    mock_network = "not_a_network"

    with pytest.raises(NotImplementedError):
        create_project(
            mock_conn,
            mock_project,
            mock_email,
            mock_description,
            mock_user_domain,
            mock_network,
        )


@patch("workflows.create_project.Networks.from_string")
def test_project_create_raise_unknown_network_type_enum(mock_from_string):
    """
    Test project creation with an unknown network type.
    """
    mock_conn = MagicMock()
    mock_project = "mock_project"
    mock_email = "email@example.com"
    mock_description = "mock_description"
    mock_user_domain = "stfc"
    mock_network = "mock_network"
    mock_from_string.return_value = NonCallableMock()

    with pytest.raises(NotImplementedError):
        create_project(
            mock_conn,
            mock_project,
            mock_email,
            mock_description,
            mock_user_domain,
            mock_network,
        )
