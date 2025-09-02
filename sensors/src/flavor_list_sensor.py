from st2reactor.sensor.base import PollingSensor
from openstack_api.openstack_flavor import OpenstackFlavor


class FlavorListSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=10):
        super().__init__(
            sensor_service=sensor_service, config=config, poll_interval=poll_interval
        )
        self._api = OpenstackFlavor()
        self._log = self._sensor_service.get_logger(__name__)
        self._cloud = self._config["sensor_dest_cloud"]

    def setup(self):
        """
        Sets up the sensor.
        """
        self._log.info(f"Destination Cloud: {self._cloud}")

    def poll(self):
        self._log.info("Polling for  flavors.")

        dest_flavors = self._api.list_flavors(self._cloud)

        self._log.info("Dispatching trigger for flavor list.")
        payload = {
            "dest_flavors": [dest.name for dest in dest_flavors],
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
