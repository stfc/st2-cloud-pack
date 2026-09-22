from time import sleep

from apis.openstack_api.enums.hypervisor_enums import HypervisorAction
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
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)
        self.cloud_account = self.config["sensor_cloud_account"]
        self.uptime_limit = self.config["hypervisor_sensor"].get("uptime_limit", 180)

    def setup(self):
        """
        Stub
        """

    def poll(self):
        """
        Polls the state of hypervisors.
        """
        self._logger.info("HypervisorSensor querying openstack")

        data = query_hypervisor_state(self.cloud_account)

        # TODO: Add a prioritize function which will order the list
        #       of hypervisors in data by maintenance priority, e.g.
        #       FW update date, OS version etc.

        for hypervisor in data:
            if not isinstance(hypervisor, dict):
                continue
            hypervisor = Hypervisor.from_dict(self.cloud_account, hypervisor)
            self._logger.info(f"evaluating action for {hypervisor.name}")
            action = hypervisor.take_action(uptime_limit=self.uptime_limit)
            self._logger.info(f"{hypervisor.name}: {action.name}")
            if action is not HypervisorAction.NOOP:
                payload = {
                    "hypervisor_name": hypervisor.name,
                    "cloud_account": self.cloud_account,
                    "action": action.name,
                }
                self._logger.info(
                    f"Dispatching action {action.name} for {hypervisor.name}"
                )
                self.sensor_service.dispatch(
                    trigger="stackstorm_openstack.hypervisor.state_change",
                    payload=payload,
                )

                # If a drain was triggered wait a min to allow it
                # to be disabled before moving on to ensure accurate
                # capacity calculations
                if action is HypervisorAction.DRAIN:
                    self._logger.info(
                        f"Waiting for drain of {hypervisor.name} to be started"
                    )
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
