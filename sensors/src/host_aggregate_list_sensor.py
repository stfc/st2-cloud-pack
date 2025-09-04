from openstack_api.openstack_connection import OpenstackConnection
from st2reactor.sensor.base import PollingSensor


class HostAggregateSensor(PollingSensor):
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

    def __init__(self, sensor_service, config=None, poll_interval=None):
        super().__init__(
            sensor_service=sensor_service, config=config, poll_interval=poll_interval
        )
        self._log = self._sensor_service.get_logger(__name__)
        self.dest_cloud_account = self.config["sensor_dest_cloud"]

    def setup(self):
        """
        Stub
        """

    def poll(self):
        """
        Polls the dev cloud host aggregates and dispatches a payload containing
        a list of aggregates.
        """
        with OpenstackConnection(self.dest_cloud_account) as conn:
            self._log.info(f"Destination Cloud: {self.dest_cloud_account}")
            self._log.info("Polling for destination aggregates.")

            # Returns a generator, consume it into a list and convert each item to a dict
            dest_aggregates = [agg.to_dict() for agg in conn.compute.aggregates()]

            self._log.info("Dispatching trigger for aggregate list.")

            payload = {"dest_aggregates": dest_aggregates}

            self.sensor_service.dispatch(
                trigger="stackstorm_openstack.aggregate.aggregate_list",
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
