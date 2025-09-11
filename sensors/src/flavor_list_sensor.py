from st2reactor.sensor.base import PollingSensor
from openstack_api.openstack_connection import OpenstackConnection
from deepdiff import DeepDiff


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
        self.source_cloud_account = self.config["sensor_source_cloud"]
        self.dest_cloud_account = self.config["sensor_dest_cloud"]

    def setup(self):
        """
        Stub
        """

    def poll(self):
        """
        Polls the source cloud flavors and checks each flavor against those in the
        destination cloud. Compares the flavor properties and, where there is a difference,
        dispatches a payload containing the flavor name and the difference.
        """
        with OpenstackConnection(
            self.source_cloud_account
        ) as source_conn, OpenstackConnection(self.dest_cloud_account) as dest_conn:
            self.log.info("Polling for flavors.")

            source_flavors = {
                flavor.name: flavor for flavor in source_conn.list_flavors()
            }
            dest_flavors = {flavor.name: flavor for flavor in dest_conn.list_flavors()}

            for flavor_name, source_flavor in source_flavors.items():
                dest_flavor = dest_flavors.get(flavor_name)

                if not dest_flavor:
                    mismatch = (
                        f"Flavor does not exist in target cloud: {source_flavor.name}"
                    )
                    self.log.info(mismatch)

                    self.dispatch_trigger(
                        flavor_name=source_flavor.name,
                        source_flavor_id=source_flavor.id,
                        dest_flavor_id=None,
                        mismatch=mismatch,
                    )
                    continue

                self.log.info(
                    f"Checking for mismatch between source and target: {flavor_name}"
                )
                diff = DeepDiff(
                    source_flavor,
                    dest_flavor,
                    ignore_order=True,
                    threshold_to_diff_deeper=0,
                    exclude_paths={
                        "root['id']",
                        "root['location']",
                        "root['extra_specs']",
                    },
                )

                if diff:
                    mismatch = f"Mismatch in properties found: {diff.pretty()}"
                    self.log.info(mismatch)

                    self.dispatch_trigger(
                        flavor_name=source_flavor.name,
                        source_flavor_id=source_flavor.id,
                        dest_flavor_id=dest_flavor.id,
                        mismatch=mismatch,
                    )

                else:
                    self.log.info("No mismatch found.")

    def dispatch_trigger(self, **kwargs):
        payload = {**kwargs}

        self.sensor_service.dispatch(
            trigger="stackstorm_openstack.flavor.flavor_mismatch",
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
