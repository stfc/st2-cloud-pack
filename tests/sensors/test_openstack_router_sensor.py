from unittest.mock import MagicMock, patch
import pytest
from sensors.src.openstack_router_sensor import OpenstackRouterSensor


@pytest.fixture(name="sensor")
def state_sensor_fixture():
    """
    Fixture for setting up router sensor
    """
    return OpenstackRouterSensor(
        sensor_service=MagicMock(),
        config={"sensor_cloud_account": "dev"},
        poll_interval=10,
    )


@patch("sensors.src.openstack_router_sensor.check_for_internal_routers")
@patch("sensors.src.openstack_router_sensor.OpenstackConnection")
def test_poll(mock_openstack_connection, mock_check_for_internal_routers, sensor):
    """
    Test main function of sensor, polling state of hypervisor state
    """
    mock_conn = MagicMock()
    mock_openstack_connection.return_value.__enter__.return_value = mock_conn

    mock_router = MagicMock()

    mock_check_for_internal_routers.return_value = [mock_router]

    sensor.poll()

    mock_check_for_internal_routers.assert_called_once_with(mock_conn)

    expected_payload = {
        "router_id": mock_router.id,
        "router_name": mock_router.name,
        "router_description": mock_router.description,
        "project_id": mock_router.project_id,
        "created_at": mock_router.created_at,
        "status": mock_router.status,
        "gateways": mock_router.external_gateway_info.get("external_fixed_ips"),
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.openstack_router_issue",
        payload=expected_payload,
    )
