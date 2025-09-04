from st2reactor.sensor.base import PollingSensor
from openstack_api.openstack_flavor import OpenstackFlavor


class FlavorListSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=10):
        super().__init__(
            sensor_service=sensor_service, config=config, poll_interval=poll_interval
        )
        self.api = OpenstackFlavor()
        self.log = self._sensor_service.get_logger(__name__)
        self.cloud = self._config["sensor_dest_cloud"]

    def setup(self):
        """
        Stub
        """

    def poll(self):
        self.log.info(f"Destination Cloud: {self.cloud}")
        self.log.info("Polling for  flavors.")

        dest_flavors = self.api.list_flavors(self.cloud)

        self.log.info("Dispatching trigger for flavor list.")
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
