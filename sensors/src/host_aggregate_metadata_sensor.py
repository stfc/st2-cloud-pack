import tabulate

from apis.openstack_api.openstack_connection import OpenstackConnection
from apis.utils.diff_table import diff_to_tabulate_table
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
        self.source_cloud = self.config["sensor_source_cloud"]
        self.target_cloud = self.config["sensor_dest_cloud"]

    def setup(self):
        """
        Stub
        """

    def poll(self):
        """
        Polls the dev cloud host aggregates and dispatches a payload containing
        a list of aggregates.
        """
        with OpenstackConnection(self.source_cloud) as source_conn, OpenstackConnection(
            self.target_cloud
        ) as target_conn:

            source_aggregates = {
                agg.name: agg for agg in source_conn.compute.aggregates()
            }
            target_aggregates = {
                agg.name: agg for agg in target_conn.compute.aggregates()
            }

            self._log.info(
                "Compare source (%s) and target (%s) host aggregate metadata"
            )

            for aggregate_name, source_agg in source_aggregates.items():
                target_agg = target_aggregates.get(aggregate_name)

                if not target_agg:
                    self._log.info(
                        "aggregate %s doesn't exist in %s cloud",
                        aggregate_name,
                        self.target_cloud,
                    )
                    continue

                diff = diff_to_tabulate_table(
                    obj1=source_agg,
                    obj2=target_agg,
                    excluded_paths=[
                        "root['hosts']",
                        "root['created_at']",
                        "root['updated_at']",
                        "root['uuid']",
                        "root['id']",
                        "root['location']",
                    ],
                )

                if diff:

                    self._log.info(
                        "aggregate metadata mismatch between source (%s) and target (%s): %s",
                        self.source_cloud,
                        self.target_cloud,
                        aggregate_name,
                    )

                    headers = [
                        "Path",
                        self.source_cloud,
                        self.target_cloud,
                    ]

                    payload = {
                        "aggregate_name": source_agg.name,
                        "diff": tabulate.tabulate(
                            diff,
                            headers=headers,
                            tablefmt="jira",
                        ),
                    }

                    self.sensor_service.dispatch(
                        trigger="stackstorm_openstack.aggregate.metadata_mismatch",
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
