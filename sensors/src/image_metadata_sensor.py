from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_image import get_all_image_metadata
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
        Setup stuff goes here. For example, you might establish connections
        to external system once and reuse it. This is called only once by the system.
        """

    def poll(self):
        """
        Polls the dev cloud image metadata.
        """
        with OpenstackConnection(self.cloud_account) as conn:
            for image in get_all_image_metadata(conn):
                self._log.info("Dispatching trigger for image: %s", image["Image ID"])
                payload = {
                    "image_id": image["Image ID"],
                    "image_name": image["Name"],
                    "image_status": image["Status"],
                    "image_visibility": image["Visibility"],
                    "image_min_disk": image["Min Disk (GB)"],
                    "image_min_ram": image["Min RAM (MB)"],
                    "image_os_type": image["OS Type"]
                    # "image_metadata": image["Metadata"]
                }
                self.sensor_service.dispatch(
                    trigger="stackstorm_openstack.image.metadata_change",
                    payload=payload
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
