from unittest.mock import MagicMock, patch
import pytest
from sensors.src.image_metadata_sensor import ImageMetadataSensor


@pytest.fixture(name="sensor")
def metadata_sensor_fixture():
    """
    Fixture for sensor config.
    """
    return ImageMetadataSensor(
        sensor_service=MagicMock(),
        config={
            "sensor_cloud_account": "dev",
        },
        poll_interval=10,
    )


@patch("sensors.src.image_metadata_sensor.OpenstackConnection")
def test_poll(mock_openstack_connection, sensor):
    """
    Test main function of sensor, polling the dev cloud images and their metadata.
    """
    mock_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.return_value = mock_conn

    mock_image = MagicMock()
    mock_conn.image.images.return_value = [mock_image]

    sensor.poll()

    mock_conn.image.images.assert_called_once_with()

    expected_payload = {
        "image_id": mock_image.id,
        "image_name": mock_image.name,
        "image_status": mock_image.status,
        "image_visibility": mock_image.visibility,
        "image_min_disk": mock_image.min_disk,
        "image_min_ram": mock_image.min_ram,
        "image_os_type": mock_image.os_type,
        "image_metadata": mock_image.properties,
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.image.metadata_change",
        payload=expected_payload,
    )
