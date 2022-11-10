"""
Polling Sensor to query OpenStack for empty hypervisors.
"""

from st2reactor.sensor.base import PollingSensor
from st2reactor.container.sensor_wrapper import SensorService
from openstack_api.openstack_hypervisor import OpenstackHypervisor
class HypervisorPollingSensor(PollingSensor):

    def __init__(self, sensor_service, config=None, poll_interval=10):
        super().__init__(sensor_service, config, poll_interval)
        self.api = OpenstackHypervisor()
        self.sensor_service: SensorService = sensor_service
        self._log = self.sensor_service.get_logger(name=self.__class__.__name__)
        self._cloud = {"dev": None, "prod": None}
        self._environment = "dev"

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
        self._cloud["prod"] = self.sensor_service.get_value(
            "automated_hypervisor_updater.prod_cloud", local=False, decrypt=False
        )
        self._cloud["dev"] = self.sensor_service.get_value(
            "automated_hypervisor_updater.dev_cloud", local=False, decrypt=False
        )

        if self._cloud["prod"] != "not_set" and self._cloud["prod"] != None:
            self._environment = "prod"
        
        self._log.info("Environment: " + str(self._environment))
        self._log.info("Cloud to use: " + str(self._cloud[self._environment]))

    def poll(self):
        """
        Poll OpenStack for empty hypervisors and make list to pass to hypervisor_shutdown action
        """
        hvs_to_update = self.api.get_all_empty_hypervisors(self._cloud[self._environment])
        self._log.info(hvs_to_update)