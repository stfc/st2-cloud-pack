from unittest.mock import MagicMock, patch

import pytest

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


@patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
def test_poll_flavor_mismatch(mock_openstack_connection, sensor):
    """
    Test main function of sensor, detecting a mismatch between the source and target flavor.
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()

    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_flavor_dict = {
        "name": "test_flavor",
        "disk": 700,
        "ram": 91200,
        "vcpus": 12,
        "extra_specs": {
            "spec_1": "1",
        },
        "id": "0000-0000-0000-0000",
        "location": {
            "cloud": "test_cloud",
            "project": {
                "id": "1111-1111-1111-1111",
            },
        },
    }
    mock_source_flavor = MagicMock()
    mock_source_flavor.name = "test_flavor"
    mock_source_flavor.id = "0000-0000-0000-0000"
    mock_source_conn.list_flavors.return_value = [mock_source_flavor]
    mock_source_flavor.items.return_value = mock_source_flavor_dict.items()
    mock_source_flavor.to_dict.return_value = mock_source_flavor_dict

    mock_target_flavor_dict = {
        "name": "test_flavor",
        "disk": 800,
        "ram": 91300,
        "vcpus": 14,
        "extra_specs": {
            "spec_1": "1",
            "spec_2": "2",
            "spec_3": "3",
        },
        "id": "9999-9999-9999-9999",
        "location": {
            "cloud": "test_cloud",
            "project": {
                "id": "1111-1111-1111-1111",
            },
        },
    }
    mock_target_flavor = MagicMock()
    mock_target_flavor.name = "test_flavor"
    mock_target_flavor.id = "9999-9999-9999-9999"
    mock_target_conn.list_flavors.return_value = [mock_target_flavor]
    mock_target_flavor.to_dict.return_value = mock_target_flavor_dict

    sensor.poll()

    mock_source_conn.list_flavors.assert_called_once_with()
    mock_target_conn.list_flavors.assert_called_once_with()

    expected_mismatch = (
        "Mismatch in properties found: Item root['extra_specs']['spec_2'] added to dictionary.\n"
        + "Item root['extra_specs']['spec_3'] added to dictionary.\n"
        + "Value of root['disk'] changed from 700 to 800.\n"
        + "Value of root['ram'] changed from 91200 to 91300.\n"
        + "Value of root['vcpus'] changed from 12 to 14."
    )
    expected_payload = {
        "flavor_name": mock_source_flavor.name,
        "source_cloud": sensor.source_cloud,
        "target_cloud": sensor.target_cloud,
        "source_flavor_id": mock_source_flavor.id,
        "target_flavor_id": mock_target_flavor.id,
        "flavor_mismatch": expected_mismatch,
        "source_flavor_properties": str(mock_source_flavor_dict),
        "target_flavor_properties": str(mock_target_flavor_dict),
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.flavor.flavor_mismatch",
        payload=expected_payload,
    )


@patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
def test_poll_flavor_not_in_target(mock_openstack_connection, sensor):
    """
    Test main function of sensor, detecting that the source flavor does not exist in the target.
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()

    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_flavor_dict = {
        "name": "test_flavor",
        "disk": 700,
        "ram": 91200,
        "vcpus": 12,
        "extra_specs": {
            "spec_1": "1",
        },
        "id": "0000-0000-0000-0000",
        "location": {
            "cloud": "test_cloud",
            "project": {
                "id": "1111-1111-1111-1111",
            },
        },
    }
    mock_source_flavor = MagicMock()
    mock_source_flavor.name = "test_flavor"
    mock_source_flavor.id = "0000-0000-0000-0000"
    mock_source_conn.list_flavors.return_value = [mock_source_flavor]
    mock_source_flavor.items.return_value = mock_source_flavor_dict.items()
    mock_source_flavor.to_dict.return_value = mock_source_flavor_dict

    mock_target_flavor = MagicMock()
    mock_target_flavor.name = None
    mock_target_conn.list_flavors.return_value = [mock_target_flavor]

    sensor.poll()

    mock_source_conn.list_flavors.assert_called_once_with()
    mock_target_conn.list_flavors.assert_called_once_with()

    expected_mismatch = (
        f"Flavor does not exist in target cloud: {mock_source_flavor.name}"
    )
    expected_payload = {
        "flavor_name": mock_source_flavor.name,
        "source_cloud": sensor.source_cloud,
        "target_cloud": sensor.target_cloud,
        "source_flavor_id": mock_source_flavor.id,
        "target_flavor_id": None,
        "flavor_mismatch": expected_mismatch,
        "source_flavor_properties": str(mock_source_flavor_dict),
        "target_flavor_properties": None,
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.flavor.flavor_mismatch",
        payload=expected_payload,
    )


@patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
def test_poll_flavor_match(mock_openstack_connection, sensor):
    """
    Test main function of sensor, detecting no mismatch between the source and target flavor.
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()

    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_flavor_dict = {
        "name": "test_flavor",
        "disk": 700,
        "ram": 91200,
        "vcpus": 12,
        "extra_specs": {
            "spec_1": "1",
        },
        "id": "0000-0000-0000-0000",
        "location": {
            "cloud": "test_cloud",
            "project": {
                "id": "1111-1111-1111-1111",
            },
        },
    }
    mock_source_flavor = MagicMock()
    mock_source_flavor.name = "test_flavor"
    mock_source_flavor.id = "0000-0000-0000-0000"
    mock_source_conn.list_flavors.return_value = [mock_source_flavor]
    mock_source_flavor.items.return_value = mock_source_flavor_dict.items()
    mock_source_flavor.to_dict.return_value = mock_source_flavor_dict

    mock_target_flavor_dict = {
        "name": "test_flavor",
        "disk": 700,
        "ram": 91200,
        "vcpus": 12,
        "extra_specs": {
            "spec_1": "1",
        },
        "id": "9999-9999-9999-9999",
        "location": {
            "cloud": "test_cloud",
            "project": {
                "id": "1111-1111-1111-1111",
            },
        },
    }
    mock_target_flavor = MagicMock()
    mock_target_flavor.name = "test_flavor"
    mock_target_flavor.id = "9999-9999-9999-9999"
    mock_target_conn.list_flavors.return_value = [mock_target_flavor]
    mock_target_flavor.to_dict.return_value = mock_target_flavor_dict

    sensor.poll()

    mock_source_conn.list_flavors.assert_called_once_with()
    mock_target_conn.list_flavors.assert_called_once_with()

    sensor.sensor_service.dispatch.assert_not_called()
