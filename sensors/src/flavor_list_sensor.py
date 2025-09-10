import json
import datetime

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
            self.log.info("Source: %s", self.source_cloud_account)
            self.log.info("Destination: %s", self.dest_cloud_account)

            self.log.info("Polling for flavors.")

            source_flavors = {
                flavor.name: flavor.name for flavor in source_conn.list_flavors()
            }
            dest_flavors = {
                flavor.name: flavor.name for flavor in dest_conn.list_flavors()
            }

            sync_date = str(datetime.datetime.now())
            self.log.info("Sync date: %s", sync_date)

            for flavor_name, source_flavor in source_flavors.items():
                dest_flavor = dest_flavors.get(flavor_name)

                if not dest_flavor:
                    self.log.info(
                        "Flavor %s doesn't exist in the target cloud.", flavor_name
                    )
                    continue

                diff = DeepDiff(
                    source_flavor,
                    dest_flavor,
                    ignore_order=True,
                    threshold_to_diff_deeper=0,
                    exclude_paths={
                        # "root['id']",
                        "root['location']",
                        "root['extra_specs']",
                    },
                )

                # self.log.info(
                #     "Checking differences between flavors\n %s", diff.pretty()
                # )
                self.log.info(
                    "Checking differences between prod and dev %s", flavor_name
                )

                if diff:

                    self.log.info(
                        "Flavor mismatch between source and target: %s", flavor_name
                    )

                    payload = {
                        "flavor_name": source_flavor.name,
                        "dest_cloud": {"name": self.dest_cloud_account},
                        "source_flavor_properties": source_flavor,
                        "dest_flavor_properties": dest_flavor,
                        "sync_date": sync_date,
                    }

                    self.sensor_service.dispatch(
                        trigger="stackstorm_openstack.flavor.flavor_mismatch",
                        payload=payload,
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
