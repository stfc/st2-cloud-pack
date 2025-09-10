import json

from st2reactor.sensor.base import PollingSensor
from apis.openstack_api.openstack_connection import OpenstackConnection


class FlavorListSensor(PollingSensor):
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

    def __init__(self, sensor_service, config=None, poll_interval=10):
        super().__init__(
            sensor_service=sensor_service, config=config, poll_interval=poll_interval
        )
        self.log = self._sensor_service.get_logger(__name__)
        self.dest_cloud_account = self.config["sensor_dest_cloud"]

    def setup(self):
        """
        Stub
        """

    def poll(self):
        """
        Polls the dev cloud flavors and dispatches a payload containing
        a list of flavors.
        """
        with OpenstackConnection(self.dest_cloud_account) as conn:
            self.log.info(f"Destination Cloud: {self.dest_cloud_account}")
            self.log.info("Polling for flavors.")

            dest_flavors = [
                json.dumps(flavor.to_dict()) for flavor in conn.list_flavors()
            ]

            self.log.info("Dispatching trigger for flavor list.")

            payload = {
                "dest_flavors": dest_flavors,
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
