from apis.openstack_api.openstack_connection import OpenstackConnection
from st2reactor.sensor.base import PollingSensor
from deepdiff import DeepDiff


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
        self.source_cloud = self.config["image_sensor"]["source_cloud_account"]
        self.target_cloud = self.config["image_sensor"]["target_cloud_account"]

    def setup(self):
        """
        Stub
        """

    def poll(self):
        """
        Polls the source cloud images and lookup the relevant image in target for each image
        Compare the image metadata between source and target cloud and dispatch a payload
        containing the image's properties/metadata and the difference.

        """
        with OpenstackConnection(self.source_cloud) as source_conn, OpenstackConnection(
            self.target_cloud
        ) as target_conn:

            source_images = {
                img.name: img for img in source_conn.image.images(status="active")
            }
            target_images = {img.name: img for img in target_conn.image.images()}

            self._log.info("Compare source and target metadata")

            for image_name, source_img in source_images.items():
                target_img = target_images.get(image_name)

                if not target_img:
                    self._log.info("Image %s doesn't exist in target cloud", image_name)
                    continue

                diff = DeepDiff(
                    source_img.properties,
                    target_img.properties,
                    ignore_order=True,
                    threshold_to_diff_deeper=0,
                    exclude_paths={
                        "root['instance_uuid']",
                        "root['location']['project']['id']",
                        "root['location']['cloud']",
                        "root['owner_id']",
                        "root['owner']",
                        "root['file']",
                        "root['direct_url']",
                        "root['locations']",
                        "root['id']",
                        "root['created_at']",
                        "root['updated_at']",
                    },
                )

                self._log.info(
                    "Checking for the difference between metadata %s", diff.pretty()
                )

                if diff:

                    self._log.info(
                        "Image metadata mismatch between source and target: %s",
                        image_name,
                    )

                    payload = {
                        "image_name": source_img.name,
                        "source_metadata": source_img.properties,
                        "target_cloud": {"name": self.target_cloud},
                    }

                    self.sensor_service.dispatch(
                        trigger="stackstorm_openstack.image.metadata_mismatch",
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
