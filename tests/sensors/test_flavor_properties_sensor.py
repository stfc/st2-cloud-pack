from unittest.mock import MagicMock, patch

import pytest
import tabulate

from sensors.src.flavor_properties_sensor import FlavorPropertiesSensor


@pytest.fixture(name="sensor")
def flavor_properties_sensor_fixture():
    """
    Fixture for sensor config.
    """
    return FlavorPropertiesSensor(
        sensor_service=MagicMock(),
        config={
            "flavor_sensor": {
                "source_cloud_account": "prod",
                "target_cloud_account": "dev",
            }
        },
        poll_interval=10,
    )


@patch("sensors.src.flavor_properties_sensor.get_diff")
@patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
def test_poll_flavor_mismatch(mock_openstack_connection, mock_get_diff, sensor):
    """
    Test detecting a mismatch between the source and target flavor.
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_flavor = MagicMock()
    mock_source_flavor.name = "test_flavor"
    mock_source_flavor.id = "0000-0000-0000-0000"
    mock_source_flavor.to_dict.return_value = {"disk": 700, "ram": 91200, "vcpus": 12}
    mock_source_conn.list_flavors.return_value = [mock_source_flavor]

    mock_target_flavor = MagicMock()
    mock_target_flavor.name = "test_flavor"
    mock_target_flavor.id = "9999-9999-9999-9999"
    mock_target_flavor.to_dict.return_value = {"disk": 800, "ram": 91300, "vcpus": 14}
    mock_target_conn.list_flavors.return_value = [mock_target_flavor]

    # Simulate a diff
    mock_get_diff.return_value = [
        ["root['disk']", 700, 800],
        ["root['ram']", 91200, 91300],
        ["root['vcpus']", 12, 14],
    ]

    sensor.poll()

    mock_source_conn.list_flavors.assert_called_once()
    mock_target_conn.list_flavors.assert_called_once()

    expected_payload = {
        "flavor_name": "test_flavor",
        "source_cloud": sensor.source_cloud,
        "target_cloud": sensor.target_cloud,
        "source_flavor_id": "0000-0000-0000-0000",
        "target_flavor_id": "9999-9999-9999-9999",
        "diff": tabulate.tabulate(
            [
                ["root['disk']", 700, 800],
                ["root['ram']", 91200, 91300],
                ["root['vcpus']", 12, 14],
            ],
            headers=["Path", "prod", "dev"],
            tablefmt="jira",
        ),
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.flavor.flavor_mismatch",
        payload=expected_payload,
    )


@patch("sensors.src.flavor_properties_sensor.get_diff")
@patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
def test_poll_flavor_not_in_target(mock_openstack_connection, mock_get_diff, sensor):
    """
    Test detecting that the source flavor does not exist in the target.
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_flavor = MagicMock()
    mock_source_flavor.name = "test_flavor"
    mock_source_flavor.id = "0000-0000-0000-0000"
    mock_source_flavor.to_dict.return_value = {"disk": 700, "ram": 91200, "vcpus": 12}
    mock_source_conn.list_flavors.return_value = [mock_source_flavor]

    mock_target_conn.list_flavors.return_value = []

    sensor.poll()

    mock_source_conn.list_flavors.assert_called_once()
    mock_target_conn.list_flavors.assert_called_once()
    mock_get_diff.assert_not_called()

    expected_payload = {
        "flavor_name": mock_source_flavor.name,
        "source_cloud": sensor.source_cloud,
        "target_cloud": sensor.target_cloud,
        "source_flavor_id": mock_source_flavor.id,
        "target_flavor_id": None,
        "diff": tabulate.tabulate(
            [
                [
                    f"Flavor missing in {sensor.target_cloud}",
                    mock_source_flavor.id,
                    "N/A",
                ]
            ],
            headers=["Path", sensor.source_cloud, sensor.target_cloud],
            tablefmt="jira",
        ),
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.flavor.flavor_mismatch",
        payload=expected_payload,
    )


@patch("sensors.src.flavor_properties_sensor.get_diff")
@patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
def test_poll_flavor_match(mock_openstack_connection, mock_get_diff, sensor):
    """
    Test detecting no mismatch between the source and target flavor.
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_flavor = MagicMock()
    mock_source_flavor.name = "test_flavor"
    mock_source_flavor.id = "0000-0000-0000-0000"
    mock_source_flavor.to_dict.return_value = {"disk": 700, "ram": 91200, "vcpus": 12}
    mock_source_conn.list_flavors.return_value = [mock_source_flavor]

    mock_target_flavor = MagicMock()
    mock_target_flavor.name = "test_flavor"
    mock_target_flavor.id = "9999-9999-9999-9999"
    mock_target_flavor.to_dict.return_value = {"disk": 700, "ram": 91200, "vcpus": 12}
    mock_target_conn.list_flavors.return_value = [mock_target_flavor]

    # No differences
    mock_get_diff.return_value = []

    sensor.poll()

    mock_source_conn.list_flavors.assert_called_once()
    mock_target_conn.list_flavors.assert_called_once()
    sensor.sensor_service.dispatch.assert_not_called()
