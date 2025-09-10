from apis.openstack_api.openstack_connection import OpenstackConnection
from apis.openstack_api.openstack_router import check_for_internal_routers
from st2reactor.sensor.base import PollingSensor


class OpenstackRouterSensor(PollingSensor):
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
        self.cloud_account = self.config["sensor_cloud_account"]

    def setup(self):
        """
        Setup stuff goes here. For example, you might establish connections
        to external system once and reuse it. This is called only once by the system.
        """

    def poll(self):
        """
        Polls the state of hypervisors
        """
        with OpenstackConnection(self.cloud_account) as conn:
            data = check_for_internal_routers(conn)
            for router in data:
                self._log.info("Dispatching Trigger for router: %s", router.id)
                self.sensor_service.dispatch(
                    trigger="stackstorm_openstack.openstack_router_issue",
                    payload={
                        "router_id": router.id,
                        "router_name": router.name,
                        "router_description": router.description,
                        "project_id": router.project_id,
                        "created_at": router.created_at,
                        "status": router.status,
                        "gateways": router.external_gateway_info.get(
                            "external_fixed_ips"
                        ),
                    },
                )

    def cleanup(self):
        """
        This is called when the st2 system goes down. You can perform cleanup operations like
        closing the connections to external system here.
        """

    def add_trigger(self, trigger):
        """This method is called when trigger is created"""

    def update_trigger(self, trigger):
        """This method is called when trigger is updated"""

    def remove_trigger(self, trigger):
        """This method is called when trigger is deleted"""
