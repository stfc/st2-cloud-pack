"""
Polling Sensor to query OpenStack for empty hypervisors.
"""

from st2reactor.sensor.base import PollingSensor
from st2reactor.container.sensor_wrapper import SensorService
from lib.openstack_api.openstack_hypervisor import OpenstackHypervisor
class HypervisorPollingSensor(PollingSensor):

    def __init__(self, sensor_service: SensorService, config=None, poll_interval=10):
        # pylint: disable=super-with-arguments
        self.api = OpenstackHypervisor()
        self.sensor_service: SensorService = sensor_service
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)

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
        pass

    def poll(self):
        """
        Poll OpenStack for empty hypervisors and make list to pass to hypervisor_shutdown action
        """
        updateable_hvs = self.api.get_all_empty_hypervisors("admin-openstack")