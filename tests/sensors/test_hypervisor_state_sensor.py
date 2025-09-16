from unittest.mock import MagicMock, patch
import pytest
from apis.openstack_api.enums.hypervisor_states import HypervisorState
from sensors.src.hypervisor_state_sensor import HypervisorStateSensor


@pytest.fixture(name="sensor")
def state_sensor_fixture():
    """
    Fixture for sensor config
    """
    return HypervisorStateSensor(
        sensor_service=MagicMock(),
        config={
            "sensor_cloud_account": "dev",
            "hypervisor_sensor": {"uptime_limit": 180},
        },
        poll_interval=10,
    )


@patch("sensors.src.hypervisor_state_sensor.get_hypervisor_state")
@patch("sensors.src.hypervisor_state_sensor.query_hypervisor_state")
def test_poll(mock_query_hypervisor_state, mock_get_hypervisor_state, sensor):
    """
    Test main function of sensor, polling state of hypervisor state
    """
    mock_query_hypervisor_state.return_value = [
        {
            "hypervisor_name": "hv1",
            "hypervisor_uptime": "up 1000 days, 12:34",
            "hypervisor_status": "enabled",
            "hypervisor_state": "up",
            "hypervisor_server_count": 5,
        }
    ]

    sensor.sensor_service.get_value.return_value = "RUNNING"
    mock_get_hypervisor_state.return_value = HypervisorState.PENDING_MAINTENANCE

    sensor.poll()

    mock_query_hypervisor_state.assert_called_once_with("dev")

    mock_get_hypervisor_state.assert_called_once_with(
        mock_query_hypervisor_state.return_value[0], uptime_limit=180
    )

    expected_payload = {
        "hypervisor_name": "hv1",
        "previous_state": sensor.sensor_service.get_value.return_value,
        "current_state": mock_get_hypervisor_state.return_value.name,
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.hypervisor.state_change",
        payload=expected_payload,
    )
    sensor.sensor_service.set_value.assert_called_once_with(
        name="hv1", value="PENDING_MAINTENANCE", ttl=1209600
    )
