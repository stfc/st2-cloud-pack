import unittest
from unittest.mock import MagicMock, patch
from enums.hypervisor_states import HypervisorState
from sensors.src.hypervisor_state_sensor import HypervisorStateSensor


class TestHypervisorStateSensor(unittest.TestCase):
    """
    Test cases for testing hypervisor state sensor
    """

    def setUp(self):
        self.sensor_service = MagicMock()
        self.config = {
            "hypervisor_sensor": {"cloud_account": "dev", "uptime_limit": 180}
        }

        self.poll_interval = 10
        self.sensor = HypervisorStateSensor(
            self.sensor_service, self.config, self.poll_interval
        )

    @patch("sensors.src.hypervisor_state_sensor.get_hypervisor_state")
    @patch("sensors.src.hypervisor_state_sensor.query_hypervisor_state")
    def test_poll(self, mock_query_hypervisor_state, mock_get_hypervisor_state):
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

        self.sensor_service.get_value.return_value = "RUNNING"
        mock_get_hypervisor_state.return_value = HypervisorState.PENDING_MAINTENANCE

        self.sensor.poll()

        mock_query_hypervisor_state.assert_called_once_with("dev")

        mock_get_hypervisor_state.assert_called_once_with(
            mock_query_hypervisor_state.return_value[0], uptime_limit=180
        )

        expected_payload = {
            "hypervisor_name": "hv1",
            "previous_state": self.sensor_service.get_value.return_value,
            "current_state": mock_get_hypervisor_state.return_value.name,
        }

        self.sensor_service.dispatch.assert_called_once_with(
            trigger="stackstorm_openstack.hypervisor.state_change",
            payload=expected_payload,
        )
        self.sensor_service.set_value.assert_called_once_with(
            name="hv1", value="PENDING_MAINTENANCE"
        )
