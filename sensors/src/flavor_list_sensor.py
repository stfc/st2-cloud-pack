from st2reactor.sensor.base import PollingSensor
from openstack_api.openstack_flavor import OpenstackFlavor


class FlavorListSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=10):
        super().__init__(
            sensor_service=sensor_service, config=config, poll_interval=poll_interval
        )
        self._api = OpenstackFlavor()
        self._log = self._sensor_service.get_logger(__name__)
        self._cloud = {
            "source": self._config["sensor_source_cloud"],
            "destination": self._config["sensor_dest_cloud"],
        }

    def setup(self):
        """
        Sets up the sensor.
        """
        self._log.info(f"Source Cloud: {self._cloud['source']}")
        self._log.info(f"Destination Cloud: {self._cloud['destination']}")

    def poll(self):
        self._log.info("Polling for missing flavors.")
        missing_flavors = self._api.get_missing_flavors(
            source_cloud=self._cloud["source"], dest_cloud=self._cloud["destination"]
        )

        if not missing_flavors:
            self._log.info("No missing flavors found.")
            return

        self._log.info(f"Found {len(missing_flavors)}")
        self._log.info(f"Missing Flavors: {missing_flavors}")

        # source_flavors = self._api.list_flavor(self._cloud["source"])
        dest_flavors = self._api.list_flavor(self._cloud["destination"])

        self._log.info("Dispatching trigger for missing flavors")
        payload = {
            "source_flavors": dest_flavors,
            "dest_flavors": dest_flavors[0],
            "missing_flavors": missing_flavors,
        }
        self.sensor_service.dispatch(
            trigger="stackstorm_openstack.flavor.flavor_list",
            payload=payload,
        )

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
