"""
Polling Sensor to query OpenStack for empty hypervisors.
"""

from st2reactor.sensor.base import PollingSensor
from st2reactor.container.sensor_wrapper import SensorService
from lib.openstack_api.openstack_hypervisor import OpenstackHypervisor
class HypervisorPollingSensor(PollingSensor):

    def __init__(self, sensor_service, config=None, poll_interval=10):
        super().__init__(sensor_service, config, poll_interval)
        self.api = OpenstackHypervisor()
        self.sensor_service: SensorService = sensor_service
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)
        self._cloud = {"dev": None, "prod": None, "training": None}
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
        self._credentials["prod"] = self.sensor_service.get_value(
            "automatedUpdater.prod_token", local=False, decrypt=True
        )
        self._credentials["dev"] = self.sensor_service.get_value(
            "automatedUpdater.dev_token", local=False, decrypt=True
        )

    def poll(self, cloud_account):
        """
        Poll OpenStack for empty hypervisors and make list to pass to hypervisor_shutdown action
        """
        hvs_to_update = self.api.get_all_empty_hypervisors(cloud_account)
        self._logger.info(hvs_to_update)