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
            "image_sensor": {
                "source_cloud_account": "dev",
                "target_cloud_account": "prod",
            }
        },
        poll_interval=10,
    )


@patch("sensors.src.image_metadata_sensor.OpenstackConnection")
def test_poll_metadata_mismatch(mock_openstack_connection, sensor):
    """
    Test that metadata mismatch between source and target
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()

    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_image = MagicMock()
    mock_source_image.name = "ubuntu-22.04"
    mock_source_image.properties = {
        "os_type": "linux",
        "version": "22.04",
    }

    mock_target_image = MagicMock()
    mock_target_image.name = "ubuntu-22.04"
    mock_target_image.properties = {
        "os_type": "linux",
        "version": "24.04",
    }

    mock_source_conn.image.images.return_value = [mock_source_image]
    mock_target_conn.image.images.return_value = [mock_target_image]

    sensor.poll()

    mock_source_conn.image.images.assert_called_once()
    mock_target_conn.image.images.assert_called_once()

    expected_payload = {
        "image_name": mock_source_image.name,
        "source_metadata": mock_source_image.properties,
        "target_cloud": {"name": "prod"},
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.image.metadata_mismatch",
        payload=expected_payload,
    )


@patch("sensors.src.image_metadata_sensor.OpenstackConnection")
def test_poll_image_not_in_target(mock_openstack_connection, sensor):
    """
    Test that image exit in source but not in target
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()

    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_image = MagicMock()
    mock_source_image.name = "rocky-8"
    mock_source_image.properties = {
        "os_type": "linux",
    }

    mock_source_conn.image.images.return_value = [mock_source_image]
    mock_target_conn.image.images.return_value = []

    sensor.poll()

    sensor.sensor_service.dispatch.assert_not_called()


@patch("sensors.src.image_metadata_sensor.OpenstackConnection")
def test_poll_metadata_match(mock_openstack_connection, sensor):
    """
    Test that metadata match between source and target
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()

    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_image = MagicMock()
    mock_source_image.name = "rocky-9"
    mock_source_image.properties = {"os_type": "linux", "version": "9"}

    mock_target_image = MagicMock()
    mock_target_image.name = "rocky-9"
    mock_target_image.properties = {
        "os_type": "linux",
        "version": "9",
    }

    mock_source_conn.image.images.return_value = [mock_source_image]
    mock_target_conn.image.images.return_value = [mock_target_image]

    sensor.poll()

    sensor.sensor_service.dispatch.assert_not_called()
