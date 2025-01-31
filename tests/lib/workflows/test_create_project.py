from unittest.mock import MagicMock, patch

import pytest


from workflows.create_project import create_project


@patch("workflows.create_project.create_internal_project")
def test_project_create_internal_project(mock_create_internal_project):
    """
    Test project creation with internal network
    """
    mock_conn = MagicMock()
    mock_project = "mock_project"
    mock_email = "email@example.com"
    mock_description = "mock_description"
    mock_domain = "default"
    mock_network = "internal"

    create_project(
        mock_conn, mock_project, mock_email, mock_description, mock_domain, mock_network
    )

    mock_create_internal_project.assert_called_once_with(
        conn=mock_conn,
        project_name=mock_project,
        project_email=mock_email,
        project_description=mock_description,
        project_immutable=False,
        parent_id=None,
        admin_user_list=None,
        stfc_user_list=None,
    )


@patch("workflows.create_project.create_external_project")
def test_project_create_external_project(mock_create_external_project):
    """
    Test project creation with internal network
    """
    mock_conn = MagicMock()
    mock_project = "mock_project"
    mock_email = "email@example.com"
    mock_description = "mock_description"
    mock_domain = "default"
    mock_network = "external"

    create_project(
        mock_conn, mock_project, mock_email, mock_description, mock_domain, mock_network
    )

    mock_create_external_project.assert_called_once_with(
        conn=mock_conn,
        project_name=mock_project,
        project_email=mock_email,
        project_description=mock_description,
        network_name=f"{mock_project}-network",
        subnet_name=f"{mock_project}-subnet",
        router_name=f"{mock_project}-router",
        number_of_floating_ips=1,
        number_of_security_group_rules=200,
        project_immutable=False,
        parent_id=None,
        admin_user_list=None,
        stfc_user_list=None,
    )


def test_project_create_raise_not_default_domain():
    """
    Test project creation with internal network
    """
    mock_conn = MagicMock()
    mock_project = "mock_project"
    mock_email = "email@example.com"
    mock_description = "mock_description"
    mock_domain = "not_default"
    mock_network = "external"

    with pytest.raises(RuntimeError):
        create_project(
            mock_conn,
            mock_project,
            mock_email,
            mock_description,
            mock_domain,
            mock_network,
        )
