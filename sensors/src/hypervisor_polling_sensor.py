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
        self._config = self._config.get("cloud_names")
        self._cloud = {"dev": self._config.get("dev_cloud", None), "prod": self._config.get("prod_cloud", None)}
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
        Poll OpenStack for empty hypervisors and make list to pass to hypervisor_shutdown action
        """
        hvs_to_update = self.api.get_all_empty_hypervisors(self._cloud[self._environment])
        list_length = len(hvs_to_update)
        self._log.info("Hypervisor to update: " + str(hvs_to_update))
        self._log.info("Number of hypervisors possible to update: " + str(list_length))

        # TODO - Check if the hypervisor needs updating

        # Choose 75% to update
        pc_hvs_to_update = hvs_to_update[0:int(list_length*0.75)]
        
        self._log.info("Number of hypervisors to be updated: " + str(len(pc_hvs_to_update)))