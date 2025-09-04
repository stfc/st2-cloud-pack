import json
from unittest.mock import MagicMock, patch

import pytest

from sensors.src.host_aggregate_list_sensor import HostAggregateSensor


@pytest.fixture(name="sensor")
def aggregate_sensor_fixture():
    """
    Fixture for sensor config.
    """
    return HostAggregateSensor(
        sensor_service=MagicMock(),
        config={
            "sensor_dest_cloud": "dev",
        },
        poll_interval=10,
    )


@patch("sensors.src.host_aggregate_list_sensor.OpenstackConnection")
def test_poll(mock_openstack_connection, sensor):
    """
    Test main function of sensor, polling the dev cloud aggregates and their properties.
    """
    mock_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.return_value = mock_conn

    mock_aggregate = MagicMock()
    mock_aggregate.to_dict.return_value = {
        "name": "aggregate1",
        "availability_zone": "nova",
    }
    mock_conn.compute.aggregates.return_value = [mock_aggregate]

    sensor.poll()

    mock_conn.compute.aggregates.assert_called_once_with()

    expected_payload = {
        "dest_aggregates": [json.dumps(mock_aggregate.to_dict.return_value)]
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.aggregate.aggregate_list",
        payload=expected_payload,
    )
