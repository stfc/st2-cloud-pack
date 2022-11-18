"""
Polling Sensor to query OpenStack for empty hypervisors and trigger reboot of those hypervisors
"""

from st2reactor.sensor.base import PollingSensor
from openstack_api.openstack_hypervisor import OpenstackHypervisor

PERCENTAGE_TO_REBOOT = 75


class HypervisorPollingSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=10):
        super().__init__(sensor_service, config, poll_interval)
        self.api = OpenstackHypervisor()
        self._config = self._config.get("cloud_names")
        self._cloud = {
            "dev": self._config.get("dev_cloud", None),
            "prod": self._config.get("prod_cloud", None),
        }
        self._log = self.sensor_service.get_logger(name=self.__class__.__name__)
        self._environment = self._config.get("selected_env")

    # pylint: disable=missing-function-docstring
    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def cleanup(self):
        pass

    def remove_trigger(self, trigger):
        pass

    def setup(self):
        """
        Sets up the sensor
        """
        self._log.info("Environment: " + str(self._environment))
        self._log.info("Cloud to use: " + str(self._cloud[self._environment]))

    def poll(self):
        """
        Poll OpenStack for empty hypervisors and make list to pass to trigger action
        """
        empty_hvs = self.api.get_all_empty_hypervisors(self._cloud[self._environment])
        list_length = len(empty_hvs)

        self._log.info("Hypervisor to update: " + str(empty_hvs))
        self._log.info("Number of hypervisors possible to update: " + str(list_length))

        hvs_to_update = empty_hvs[0 : int(list_length * (PERCENTAGE_TO_REBOOT / 100))]
        self._log.info(
            "Number of hypervisors to be updated: " + str(len(hvs_to_update))
        )
