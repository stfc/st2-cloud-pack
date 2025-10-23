import tabulate
from apis.openstack_api.openstack_connection import OpenstackConnection
from apis.utils.diff_utils import get_diff
from st2reactor.sensor.base import PollingSensor


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
        self._log = self._sensor_service.get_logger(__name__)
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
        with OpenstackConnection(self.source_cloud) as source_conn, OpenstackConnection(
            self.target_cloud
        ) as target_conn:

            self._log.info("Polling for flavors.")

            source_flavors = {
                flavor.name: flavor for flavor in source_conn.list_flavors()
            }
            target_flavors = {
                flavor.name: flavor for flavor in target_conn.list_flavors()
            }

            for flavor_name, source_flavor in source_flavors.items():
                target_flavor = target_flavors.get(flavor_name)

                headers = ["Path", self.source_cloud, self.target_cloud]

                if not target_flavor:
                    self._log.info(
                        "Flavor %s does not exist in target cloud", flavor_name
                    )

                    payload = {
                        "flavor_name": source_flavor.name,
                        "source_cloud": self.source_cloud,
                        "target_cloud": self.target_cloud,
                        "source_flavor_id": source_flavor.id,
                        "target_flavor_id": None,
                        "diff": tabulate.tabulate(
                            [
                                [
                                    f"Flavor missing in {self.target_cloud}",
                                    source_flavor.id,
                                    "N/A",
                                ]
                            ],
                            headers=headers,
                            tablefmt="jira",
                        ),
                    }

                    self.sensor_service.dispatch(
                        trigger="stackstorm_openstack.flavor.flavor_mismatch",
                        payload=payload,
                    )
                    continue

                diff = get_diff(
                    obj1=source_flavor.to_dict(),
                    obj2=target_flavor.to_dict(),
                    exclude_paths=["root['id']", "root['location']"],
                )

                if diff:
                    self._log.info(
                        "Mismatch in properties found for flavor: %s", flavor_name
                    )

                    payload = {
                        "flavor_name": source_flavor.name,
                        "source_cloud": self.source_cloud,
                        "target_cloud": self.target_cloud,
                        "source_flavor_id": source_flavor.id,
                        "target_flavor_id": target_flavor.id,
                        "diff": tabulate.tabulate(
                            diff, headers=headers, tablefmt="jira"
                        ),
                    }

                    self.sensor_service.dispatch(
                        trigger="stackstorm_openstack.flavor.flavor_mismatch",
                        payload=payload,
                    )
                else:
                    self._log.info("No mismatch found for flavor: %s", flavor_name)

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
