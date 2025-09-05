from unittest.mock import MagicMock, patch
import pytest
from sensors.src.flavor_list_sensor import FlavorListSensor


@pytest.fixture(name="sensor")
def flavor_sensor_fixture():
    """
    Fixture for sensor config.
    """
    return FlavorListSensor(
        sensor_service=MagicMock(),
        config={
            "sensor_dest_cloud": "dev",
        },
        poll_interval=10,
    )


@patch("sensors.src.flavor_list_sensor.OpenstackConnection")
def test_poll(mock_openstack_connection, sensor):
    """
    Test main function of sensor, polling the dev cloud flavors.
    """
    mock_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.return_value = mock_conn

    mock_flavor = MagicMock()
    mock_flavor.to_dict.return_value = {
        "name": "aggregate1",
        "availability_zone": "nova",
    }
    mock_conn.list_flavors.return_value = [mock_flavor]

    sensor.poll()

    mock_conn.list_flavors.assert_called_once_with()

    expected_payload = {"dest_flavors": [mock_flavor]}

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.flavor.flavor_list",
        payload=expected_payload,
    )
