from unittest.mock import MagicMock, patch
import pytest
from deepdiff import DeepDiff
from sensors.src.image_metadata_sensor import ImageMetadataSensor


@pytest.fixture(name="sensor")
def metadata_sensor_fixture():
    """
    Fixture for sensor config.
    """
    return ImageMetadataSensor(
        sensor_service=MagicMock(),
        config={
            "source_cloud_account": "dev",
            "target_cloud_account": "prod",
        },
        poll_interval=10,
    )


@patch("sensors.src.image_metadata_sensor.OpenstackConnection")
def test_metadata_mismatch_dispatch(mock_openstack_connection, sensor):
    """
    Test metadata mismatch between source and target images

    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.return_value = [mock_source_conn, mock_target_conn]

    mock_source_image = MagicMock()
    mock_source_image.name = "ubuntu"
    mock_source_image.properties = {"os": "linux", "direct_url": "swift://something"}
    mock_source_image.id = "id-src"

    mock_target_image = MagicMock()
    mock_target_image.name = "ubuntu"
    mock_target_image.properties = {"os": "linux", "direct_url": "swift://something"}
    mock_target_image.id = "id-tgt"

    mock_source_conn.image.images.return_value = [mock_source_image]
    mock_target_conn.image.images.return_value = [mock_target_image]

    sensor.poll()

    mock_source_conn.image.images.assert_called_once_with()
    mock_target_conn.image.images.assert_called_once_with()

    expected_payload = {
        "image_name": mock_source_image.name,
        "source_metadata": mock_source_image.properties,
        "target_metadata": mock_target_image.properties,
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.image.metadata_change",
        payload=expected_payload,
    )