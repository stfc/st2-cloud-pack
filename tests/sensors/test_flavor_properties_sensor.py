import json
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


# TODO: Update unit test with comparison
@patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
def test_poll_no_mismatch(mock_openstack_connection, sensor):
    """
    Test main function of sensor, detecting no mismatch between the source and target flavor.
    """
    mock_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.return_value = mock_conn

    mock_flavor = MagicMock()
    mock_flavor.return_value = {
        "name": {
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
    }
    mock_conn.list_flavors.return_value = [mock_flavor]

    sensor.poll()

    mock_conn.list_flavors.assert_called_once_with()

    expected_payload = {"dest_flavors": [json.dumps(mock_flavor.to_dict.return_value)]}

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.flavor.properties_mismatch",
        payload=expected_payload,
    )


@patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
def test_poll_mismatch(mock_openstack_connection, sensor):
    """
    Test main function of sensor, detecting a mismatch between the source and target flavor.
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
        trigger="stackstorm_openstack.flavor.properties_mismatch",
        payload=expected_payload,
    )


@patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
def test_poll_missing_flavor(mock_openstack_connection, sensor):
    """
    Test main function of sensor, detecting that the source flavor does not exist in the target.
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
        trigger="stackstorm_openstack.flavor.properties_mismatch",
        payload=expected_payload,
    )
