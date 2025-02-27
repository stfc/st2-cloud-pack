from unittest.mock import MagicMock
from openstack_api.openstack_image import share_image_to_project


def test_share_image_to_project():
    """
    Test sharing image to project
    """
    mock_connection = MagicMock()
    mock_image_identifier = "test-image-id"
    mock_project_identifier = "test-project-id"

    mock_image = MagicMock()
    mock_destination_project = MagicMock()

    mock_connection.image.find_image.return_value = mock_image
    mock_connection.identity.find_project.return_value = mock_destination_project

    share_image_to_project(
        mock_connection, mock_image_identifier, mock_project_identifier
    )

    mock_connection.image.add_member.assert_called_once_with(
        mock_image["id"], member_id=mock_destination_project["id"]
    )
    mock_connection.image.update_member.assert_called_once_with(
        mock_destination_project["id"], mock_image["id"], status="accepted"
    )
