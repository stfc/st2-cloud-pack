import openstack

from openstack_api.openstack_image import get_image_metadata
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
        self.conn = None
        self._log = self._sensor_service.get_logger(__name__)
        self.cloud_account = self.config["sensor_cloud_account"]

    def setup(self):
        self.conn = openstack.connect(cloud='dev')

    def poll(self):
        """
        Polls the current dev cloud image metadata.
        """
        all_image_metadata = get_image_metadata(self.conn)
        payload = {"image_metadata": all_image_metadata}
        self.sensor_service.dispatch(
            trigger="stackstorm_openstack.image.metadata_change",
            payload=payload)
        self.sensor_service.set_value(
            name="dev_cloud_image_metadata",
            value=payload)

    def cleanup(self):
        """
        This is called when the st2 system goes down. You can perform cleanup operations like
        closing the connections to external system here.
        """
        self.conn.close()
        self.conn = None

    def add_trigger(self, trigger):
        """This method is called when trigger is created"""
        pass

    def update_trigger(self, trigger):
        """This method is called when trigger is updated"""
        pass

    def remove_trigger(self, trigger):
        """This method is called when trigger is deleted"""
        pass
