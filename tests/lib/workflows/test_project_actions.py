from unittest.mock import patch, MagicMock
from workflows.project_actions import delete_project


@patch("workflows.project_actions.openstack_project.delete_project")
def test_project_delete_with_confirmation(mock_api_delete_project):
    """
    Tests that project_delete function forwards on request to openstack API project_delete function
    and returns the correct status and string
    """

    mock_api_delete_project.return_value = True
    # setup input values
    mock_conn = MagicMock()
    mock_project_identifier = "project-id"

    mock_conn.identity.find_project.return_value = {
        "id": "project-id",
        "name": "project-name",
        "description": "project-description",
        "email": "example@example.com",
        "tags": [],
    }

    status, _ = delete_project(mock_conn, mock_project_identifier, delete=True)

    mock_conn.identity.find_project.assert_any_call("project-id", ignore_missing=False)
    mock_api_delete_project.assert_called_once_with(
        mock_conn, project_identifier=mock_project_identifier
    )
    assert status


@patch("workflows.project_actions.delete_project")
def test_project_delete_without_confirmation(mock_api_delete_project):
    """
    Tests that project_delete function forwards on request to openstack API project_delete function
    and returns the correct status and string
    """

    mock_api_delete_project.return_value = True
    # setup input values
    mock_conn = MagicMock()
    mock_project_identifier = "project-id"

    mock_conn.identity.find_project.return_value = {
        "id": "project-id",
        "name": "project-name",
        "description": "project-description",
        "email": "example@example.com",
    }

    status, _ = delete_project(mock_conn, mock_project_identifier, delete=False)

    mock_conn.identity.find_project.assert_called_once_with(
        "project-id", ignore_missing=False
    )
    mock_api_delete_project.assert_not_called()
    assert not status
