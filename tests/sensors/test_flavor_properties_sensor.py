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


# @patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
# def test_poll_flavor_mismatch(mock_openstack_connection, sensor):
#     """
#     Test main function of sensor, detecting a mismatch between the source and target flavor.
#     """
#     mock_conn = MagicMock()
#     mock_openstack_connection.return_value.__enter__.return_value = mock_conn

#     mock_flavor = MagicMock()
#     mock_flavor.to_dict.return_value = {
#         "name": "test_flavor",
#         "disk": 700,
#         "ram": 91200,
#         "vcpus": 12,
#         "extra_specs": {
#             "spec_1": "1",
#         },
#         "id": "0000-0000-0000-0000",
#         "location": {
#             "cloud": "test_cloud",
#             "project": {
#                 "id": "1111-1111-1111-1111",
#             },
#         },
#     }
#     mock_conn.list_flavors.return_value = [mock_flavor]

#     sensor.poll()

#     mock_conn.list_flavors.assert_called_once_with()

#     expected_payload = {"dest_flavors": [json.dumps(mock_flavor.to_dict.return_value)]}

#     sensor.sensor_service.dispatch.assert_called_once_with(
#         trigger="stackstorm_openstack.flavor.properties_mismatch",
#         payload=expected_payload,
#     )


@patch("sensors.src.flavor_properties_sensor.FlavorPropertiesSensor.dispatch_trigger")
@patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
def test_poll_flavor_not_in_target(
    mock_openstack_connection, mock_dispatch_trigger, sensor
):
    """
    Test main function of sensor, detecting that the source flavor does not exist in the target.
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()

    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_flavor = MagicMock()
    mock_source_flavor.name = "test_flavor"
    mock_source_flavor.items.return_value = {
        "test_flavor": {
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
    }

    mock_target_flavor = MagicMock()
    mock_target_flavor.name = "test_flavor"
    mock_target_flavor.items.return_value = {
        "test_flavor_2": {
            "name": "test_flavor_2",
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
    }

    mock_source_conn.list_flavors.return_value = mock_source_flavor
    mock_target_conn.list_flavors.return_value = mock_target_flavor

    sensor.poll()

    expected_payload = {
        "flavor_name": "test_flavor",
        "source_flavor_id": "0000-0000-0000-0000",
        "target_flavor_id": None,
        "mismatch": "test_flavor",
    }

    mock_dispatch_trigger.assert_called_once_with(
        trigger="stackstorm_openstack.image.metadata_mismatch",
        payload=expected_payload,
    )


@patch("sensors.src.flavor_properties_sensor.FlavorPropertiesSensor.dispatch_trigger")
@patch("sensors.src.flavor_properties_sensor.OpenstackConnection")
def test_poll_flavor_match(mock_openstack_connection, mock_dispatch_trigger, sensor):
    """
    Test main function of sensor, detecting no mismatch between the source and target flavor.
    """
    mock_source_conn = MagicMock()
    mock_target_conn = MagicMock()

    mock_openstack_connection.return_value.__enter__.side_effect = [
        mock_source_conn,
        mock_target_conn,
    ]

    mock_source_flavor = MagicMock()
    mock_source_flavor.name = "test_flavor"
    mock_source_flavor.items.return_value = {
        "test_flavor": {
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
    }

    mock_target_flavor = MagicMock()
    mock_target_flavor.name = "test_flavor"
    mock_target_flavor.items.return_value = {
        "test_flavor": {
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
    }

    mock_source_conn.list_flavors.return_value = mock_source_flavor
    mock_target_conn.list_flavors.return_value = mock_target_flavor

    sensor.poll()

    mock_source_conn.list_flavors.assert_called_once_with()
    mock_target_conn.list_flavors.assert_called_once_with()

    mock_dispatch_trigger.assert_not_called()
