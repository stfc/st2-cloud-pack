from unittest.mock import MagicMock, patch

import pytest

from sensors.src.host_aggregate_metadata_sensor import HostAggregateSensor


@pytest.fixture(name="sensor")
def aggregate_sensor_fixture():
    """
    Fixture for sensor config.
    """
    return HostAggregateSensor(
        sensor_service=MagicMock(),
        config={
            "sensor_source_cloud": "dev",
            "sensor_dest_cloud": "prod",
        },
        poll_interval=10,
    )


@patch("sensors.src.host_aggregate_metadata_sensor.tabulate")
@patch("sensors.src.host_aggregate_metadata_sensor.get_diff")
@patch("sensors.src.host_aggregate_metadata_sensor.OpenstackConnection")
def test_poll_mismatch(mock_openstack_connection, mock_get_diff, mock_tabulate, sensor):
    """
    Test main function of sensor, polling the dev cloud aggregates and their properties.
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()

    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_aggregate = MagicMock()
    mock_source_aggregate.name = "aggregate1"
    mock_source_aggregate.availability_zone = "nova"

    mock_target_aggregate = MagicMock()
    mock_target_aggregate.name = "aggregate1"
    mock_target_aggregate.availability_zone = "ceph"

    mock_source_conn.compute.aggregates.return_value = [mock_source_aggregate]
    mock_target_conn.compute.aggregates.return_value = [mock_target_aggregate]
    mock_diff = mock_get_diff.return_value

    sensor.poll()

    mock_source_conn.compute.aggregates.assert_called_once_with()
    mock_target_conn.compute.aggregates.assert_called_once_with()

    expected_payload = {
        "aggregate_name": mock_source_aggregate.name,
        "diff": mock_tabulate.tabulate(
            mock_diff,
            headers=["Path", "dev", "prod"],
            tablefmt="jira",
        ),
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.aggregate.metadata_mismatch",
        payload=expected_payload,
    )


@patch("sensors.src.host_aggregate_metadata_sensor.OpenstackConnection")
def test_poll_match(mock_openstack_connection, sensor):
    """
    Test main function of sensor, polling the dev cloud aggregates and their properties.
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()

    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_aggregate = MagicMock()
    mock_source_aggregate.name = "aggregate1"
    mock_source_aggregate.availability_zone = "nova"

    mock_source_conn.compute.aggregates.return_value = [mock_source_aggregate]
    mock_target_conn.compute.aggregates.return_value = [mock_source_aggregate]

    sensor.poll()

    mock_source_conn.compute.aggregates.assert_called_once_with()
    mock_target_conn.compute.aggregates.assert_called_once_with()

    sensor.sensor_service.dispatch.assert_not_called()


@patch("sensors.src.host_aggregate_metadata_sensor.OpenstackConnection")
def test_poll_not_exist_in_target(mock_openstack_connection, sensor):
    """
    Test main function of sensor, polling the dev cloud aggregates and their properties.
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()

    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_aggregate = MagicMock()
    mock_source_aggregate.name = "aggregate1"
    mock_source_aggregate.availability_zone = "nova"

    mock_target_aggregate = MagicMock()
    mock_target_aggregate.name = "aggregate2"
    mock_target_aggregate.availability_zone = "ceph"

    mock_source_conn.compute.aggregates.return_value = [mock_source_aggregate]
    mock_target_conn.compute.aggregates.return_value = [mock_target_aggregate]

    sensor.poll()

    mock_source_conn.compute.aggregates.assert_called_once_with()
    mock_target_conn.compute.aggregates.assert_called_once_with()

    sensor.sensor_service.dispatch.assert_not_called()
