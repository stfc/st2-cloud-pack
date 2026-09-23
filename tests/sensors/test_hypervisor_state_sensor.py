from unittest.mock import MagicMock, patch

import pytest
from apis.openstack_api.enums.hypervisor_enums import HypervisorAction

from apis.openstack_api.openstack_hypervisor import Hypervisor
from sensors.src.hypervisor_state_sensor import HypervisorStateSensor


@pytest.fixture(autouse=True)
def patch_sleep():
    with patch("time.sleep", return_value=None):
        yield


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


@patch("time.sleep")
@patch.object(Hypervisor, "from_dict")
@patch("sensors.src.hypervisor_state_sensor.query_hypervisor_state")
@pytest.mark.parametrize("action", ["DRAIN", "PATCH"])
def test_poll(mock_query_hypervisor_state, mock_from_dict, mock_sleep, action, sensor):
    """
    Test main function of sensor, polling state of hypervisor state
    """
    mock_hypervisor = MagicMock()
    mock_hypervisor.name = "hv1"
    mock_from_dict.return_value = mock_hypervisor
    mock_query_hypervisor_state.return_value = [{"hypervisor_name": "hv1"}]

    mock_hypervisor.take_action.return_value = HypervisorAction[action]

    sensor.poll()

    mock_query_hypervisor_state.assert_called_once_with("dev")

    mock_hypervisor.take_action.assert_called_once_with(uptime_limit=180)

    expected_payload = {
        "hypervisor_name": mock_hypervisor.name,
        "cloud_account": "dev",
        "action": action,
    }

    sensor.sensor_service.dispatch.assert_called_once_with(
        trigger="stackstorm_openstack.hypervisor.state_change",
        payload=expected_payload,
    )

    if action == "DRAIN":
        mock_sleep.assert_called_once_with(60)
    else:
        mock_sleep.assert_not_called()


@patch.object(Hypervisor, "from_dict")
@patch("sensors.src.hypervisor_state_sensor.query_hypervisor_state")
def test_poll_no_action(mock_query_hypervisor_state, mock_from_dict, sensor):
    """
    Test poll does nothing if hypervisor state hasn't changed
    """
    mock_hypervisor = MagicMock()
    mock_hypervisor.name = "hv1"
    mock_from_dict.return_value = mock_hypervisor

    mock_query_hypervisor_state.return_value = [{"hypervisor_name": "hv1"}]

    mock_hypervisor.take_action.return_value = HypervisorAction.NOOP

    sensor.poll()

    # Should call these
    mock_query_hypervisor_state.assert_called_once()
    mock_hypervisor.take_action.assert_called_once_with(uptime_limit=180)

    # Should NOT call these
    sensor.sensor_service.dispatch.assert_not_called()
    sensor.sensor_service.set_value.assert_not_called()


def test_setup(sensor):
    """
    Ensure setup() can be called without error
    """
    sensor.setup()


@patch("time.sleep")
@patch.object(Hypervisor, "from_dict")
@patch("sensors.src.hypervisor_state_sensor.query_hypervisor_state")
def test_poll_skips_non_dict(
    mock_query_hypervisor_state, mock_get_hypervisor_state, sensor
):
    """
    Test that non-dict entries in hypervisor list are skipped
    """
    mock_query_hypervisor_state.return_value = ["not_a_dict"]

    sensor.poll()

    mock_get_hypervisor_state.assert_not_called()
    sensor.sensor_service.dispatch.assert_not_called()
    sensor.sensor_service.set_value.assert_not_called()
