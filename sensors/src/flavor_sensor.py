"""
Polling Sensor to identify if there are any missing Flavors
"""

from st2reactor.sensor.base import PollingSensor
from openstack_api.openstack_flavor import OpenstackFlavor


class FlavorPollingSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=10):
        super().__init__(sensor_service, config, poll_interval)
        self.api = OpenstackFlavor()
        self._cloud = {
            "source": self._config.get("source_cloud", None),
            "destination": self._config.get("dest_cloud", None),
        }
        self._log = self.sensor_service.get_logger(name=self._class_._name_)

    def poll(self):
        missing_flavors = self._api.get_missing_flavors(
            source_cloud=self._cloud["source"], dest_cloud=self._cloud["destination"]
        )

        if not missing_flavors:
            return

        self._log.info(f"Found {len(missing_flavors)}")
        self._log.info(f"Missing Flavors: {missing_flavors}")

    def setup(self):
        """
        Sets up the sensor
        """
        self._log.info(f"Source Cloud: {self._cloud['source']}")
        self._log.info(f"Destination Cloud: {self._cloud['destination']}")

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
