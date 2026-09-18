from time import sleep

import openstack

from apis.openstack_api.openstack_hypervisor import Hypervisor
from apis.openstack_query_api.hypervisor_queries import query_hypervisor_state
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
        self.cloud_account = self.config["sensor_cloud_account"]
        self.uptime_limit = self.config["hypervisor_sensor"].get("uptime_limit", 180)
        self.state_expire_after = self.config["hypervisor_sensor"].get(
            "state_expire_after", 1209600  # 2 weeks in seconds
        )
        self.conn = openstack.connect(self.cloud_account)

    def setup(self):
        """
        Stub
        """

    def poll(self):
        """
        Polls the state of hypervisors.
        """

        data = query_hypervisor_state(self.cloud_account)
        for hypervisor in data:
            if not isinstance(hypervisor, dict):
                continue
            hypervisor = Hypervisor().from_dict(hypervisor)
            current_state = hypervisor.get_hypervisor_state(
                conn=self.conn, uptime_limit=self.uptime_limit
            )

            prev_state = self.sensor_service.get_value(name=hypervisor.name)

            if not prev_state == current_state.name:
                payload = {
                    "hypervisor_name": hypervisor.name,
                    "previous_state": prev_state,
                    "current_state": current_state.name,
                }
                self.sensor_service.dispatch(
                    trigger="stackstorm_openstack.hypervisor.state_change",
                    payload=payload,
                )
                self.sensor_service.set_value(
                    name=hypervisor.name,
                    value=current_state.name,
                    ttl=self.state_expire_after,
                )

                # If a drain was triggered wait a min to allow it
                # to be disabled before moving on to ensure accurate
                # capacity calculations
                if current_state.name == "START_DRAIN":
                    sleep(60)

    def cleanup(self):
        """
        Stub
        """

    def add_trigger(self, trigger):
        """
        Stub
        """

    def update_trigger(self, trigger):
        """
        Stub
        """

    def remove_trigger(self, trigger):
        """
        Stub
        """
