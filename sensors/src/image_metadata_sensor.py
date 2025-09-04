from openstack_api.openstack_connection import OpenstackConnection
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
        """
        Stub
        """

    def poll(self):
        """
        Polls the dev cloud images and for each image dispatches a payload containing
        the image's properties/metadata.
        """
        with OpenstackConnection(self.cloud_account) as conn:
            for image in conn.image.images():
                self._log.info("Dispatching trigger for image: %s", image.id)
                payload = {
                    "image_id": image.id,
                    "image_name": image.name,
                    "image_status": image.status,
                    "image_visibility": image.visibility,
                    "image_min_disk": image.min_disk,
                    "image_min_ram": image.min_ram,
                    "image_os_type": image.os_type,
                    "image_metadata": image.properties,
                }
                self.sensor_service.dispatch(
                    trigger="stackstorm_openstack.image.metadata_change",
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
