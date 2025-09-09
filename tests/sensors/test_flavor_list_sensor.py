import json
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
            "sensor_source_cloud": "prod",
            "sensor_dest_cloud": "dev",
        },
        poll_interval=10,
    )


# TODO: Update unit test with comparison
@patch("sensors.src.flavor_list_sensor.OpenstackConnection")
def test_poll(mock_openstack_connection, sensor):
    """
    Test main function of sensor, polling the dev cloud flavors.
    """
    mock_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.return_value = mock_conn

    mock_flavor = MagicMock()
    mock_flavor.to_dict.return_value = {
        "name": "test_flavor",
        "original_name": None,
        "description": None,
        "disk": 700,
        "is_public": False,
        "ram": 91200,
        "vcpus": 12,
        "swap": 0,
        "ephemeral": 0,
        "is_disabled": False,
        "rxtx_factor": 1.0,
        "extra_specs": {
            "spec_1": "1",
            "spec_2": "2",
            "spec_3": "3",
        },
        "id": "0000-0000-0000-0000",
        "location": {
            "cloud": "test_cloud",
            "region_name": "test_region",
            "zone": None,
            "project": {
                "id": "1111-1111-1111-1111",
                "name": "test_admin",
                "domain_id": None,
                "domain_name": None,
            },
        },
    }
    mock_conn.list_flavors.return_value = [mock_flavor]

    sensor.poll()

    mock_conn.list_flavors.assert_called_once_with()

    expected_payload = {"dest_flavors": [json.dumps(mock_flavor.to_dict.return_value)]}

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.flavor.flavor_list",
        payload=expected_payload,
    )
