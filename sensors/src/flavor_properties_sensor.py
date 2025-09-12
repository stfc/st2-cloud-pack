from openstack_api.openstack_connection import OpenstackConnection
from st2reactor.sensor.base import PollingSensor
from deepdiff import DeepDiff


class FlavorPropertiesSensor(PollingSensor):
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
        self.source_cloud = self.config["flavor_sensor"]["source_cloud_account"]
        self.target_cloud = self.config["flavor_sensor"]["target_cloud_account"]

    def setup(self):
        """
        Stub
        """

    def poll(self):
        """
        Polls the source cloud flavors and checks each flavor against those in the
        target cloud. Compares the flavor properties and, where there is a difference or
        the flavor does not exist, dispatches a payload containing the flavor name, IDs, and the mismatch.
        """

        def dispatch_trigger(**kwargs):
            """
            Creates a payload and dispatches it alongside a trigger using the sensor service.
            """
            payload = {**kwargs}

            self.sensor_service.dispatch(
                trigger="stackstorm_openstack.flavor.flavor_mismatch",
                payload=payload,
            )

        with OpenstackConnection(self.source_cloud) as source_conn, OpenstackConnection(
            self.target_cloud
        ) as target_conn:
            self.log.info("Polling for flavors.")

            source_flavors = {
                flavor.name: flavor for flavor in source_conn.list_flavors()
            }
            target_flavors = {
                flavor.name: flavor for flavor in target_conn.list_flavors()
            }

            self.log.info(f"source_flavors: {source_flavors}")

            for flavor_name, source_flavor in source_flavors.items():
                target_flavor = target_flavors.get(flavor_name)

                if not target_flavor:
                    mismatch = (
                        f"Flavor does not exist in target cloud: {source_flavor.name}"
                    )
                    self.log.info(mismatch)

                    dispatch_trigger(
                        flavor_name=source_flavor.name,
                        source_flavor_id=source_flavor.id,
                        target_flavor_id=None,
                        mismatch=mismatch,
                    )
                    continue

                self.log.info(
                    f"Checking for mismatch between source and target: {flavor_name}"
                )
                diff = DeepDiff(
                    source_flavor.to_dict(),
                    target_flavor.to_dict(),
                    ignore_order=True,
                    threshold_to_diff_deeper=0,
                    exclude_paths={
                        "root['id']",
                        "root['location']",
                    },
                )

                if diff:
                    mismatch = f"Mismatch in properties found: {diff.pretty()}"
                    self.log.info(mismatch)

                    dispatch_trigger(
                        flavor_name=source_flavor.name,
                        source_flavor_id=source_flavor.id,
                        target_flavor_id=target_flavor.id,
                        mismatch=mismatch,
                    )

                else:
                    self.log.info("No mismatch found.")

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
