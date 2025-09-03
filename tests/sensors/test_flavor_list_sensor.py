from unittest.mock import MagicMock, patch
import pytest
from sensors.src.flavor_list_sensor import FlavorListSensor
from openstack_api.openstack_flavor import OpenstackFlavor


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


@patch("sensors.src.flavor_list_sensor.OpenstackFlavor")
def test_poll(mock_openstack_flavor, sensor):
    """
    Test main function of sensor, polling the dev cloud flavors.
    """
    mock_flavor = MagicMock()
    mock_openstack_flavor.list_flavors.return_value = [mock_flavor]

    sensor.poll()

    mock_openstack_flavor.list_flavors.assert_called_once_with()

    expected_payload = {"dest_flavors": mock_flavor.name}

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.flavor.flavor_list",
        payload=expected_payload,
    )
