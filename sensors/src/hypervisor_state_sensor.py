from openstack_api.openstack_hypervisor import get_hypervisor_state
from openstack_query_api.hypervisor_queries import query_hypervisor_state
from st2reactor.sensor.base import PollingSensor


class HypervisorStateSensor(PollingSensor):
    """
    * self.sensor_service
        - provides utilities like
            get_logger() for writing to logs.
            dispatch() for dispatching triggers into the system.
    * self._config
        - contains configuration that was specified as
          config.yaml in the pack.
    * self._poll_interval
        - indicates the interval between two successive poll() calls.
    """

    def __init__(self, sensor_service, config=None, poll_interval=None):
        super().__init__(
            sensor_service=sensor_service, config=config, poll_interval=poll_interval
        )
        self._log = self._sensor_service.get_logger(__name__)
        self.cloud_account = self.config["hypervisor_sensor"].get(
            "cloud_account", "dev"
        )
        self.uptime_limit = self.config["hypervisor_sensor"].get("uptime_limit", 180)

    def setup(self):
        pass

    def poll(self):
        """
        Polls the state of hypervisors
        """

        data = query_hypervisor_state(self.cloud_account)

        for hypervisor in data:
            current_state = get_hypervisor_state(
                hypervisor, uptime_limit=self.uptime_limit
            )

            prev_state = self.sensor_service.get_value(
                name=hypervisor["hypervisor_name"]
            )

            if not prev_state == current_state:
                payload = {
                    "hypervisor_name": hypervisor["hypervisor_name"],
                    "previous_state": prev_state,
                    "current_state": current_state,
                }
                self.sensor_service.dispatch(
                    trigger="stackstorm_openstack.hypervisor.state_change",
                    payload=payload,
                )

            self.sensor_service.set_value(
                name=hypervisor["hypervisor_name"], value=current_state
            )

    def cleanup(self):
        """
        This is called when the st2 system goes down. You can perform cleanup operations like
        closing the connections to external system here.
        """

    def add_trigger(self, trigger):
        """This method is called when trigger is created"""

    def update_trigger(self, trigger):
        """This method is called when trigger is updated"""

    def remove_trigger(self, trigger):
        """This method is called when trigger is deleted"""
