from openstack_api.openstack_image import get_image_metadata
from openstack_query_api.image_queries import query_image_metadata
from st2reactor.sensor.base import PollingSensor


class ImageMetadataSensor(PollingSensor):
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
        pass

    def poll(self):
        """
        Polls the metadata of images
        """

        data = query_image_metadata(self.cloud_account)
        for image in data:
            if not isinstance(image, dict):
                continue
            current_state = get_image_metadata()

            payload = {
                "hypervisor_name": hypervisor["hypervisor_name"],
                "previous_state": prev_state,
                "current_state": current_state.name,
            }
            self.sensor_service.dispatch(
                trigger="stackstorm_openstack.hypervisor.state_change",
                payload=payload,
            )
            self.sensor_service.set_value(
                name=hypervisor["hypervisor_name"],
                value=current_state.name,
                ttl=self.state_expire_after,
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
