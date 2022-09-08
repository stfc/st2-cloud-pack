from typing import Dict, List, Callable

from openstack_action import OpenstackAction
from openstack_api.openstack_image import OpenstackImage
from openstack_api.openstack_query import OpenstackQuery


class ImageActions(OpenstackAction):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._image_api: OpenstackImage = config.get(
            "openstack_image_api", OpenstackImage()
        )
        self._query_api: OpenstackQuery = config.get(
            "openstack_query_api", OpenstackQuery()
        )

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    # pylint:disable=too-many-arguments
    def image_list(
        self,
        cloud_account: str,
        project_identifier: str,
        query_preset: str,
        properties_to_select: List[str],
        group_by: str,
        get_html: bool,
        **kwargs,
    ) -> str:
        """
        Finds all images belonging to a project (or all images if project is empty)
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: The project this applies to (or empty for all images)
        :param query_preset: The query to use when searching for images
        :param properties_to_select: The list of properties to select and output from the found images
        :param group_by: Property to group returned results - can be empty for no grouping
        :param get_html: When True tables returned are in html format
        :return: (String or Dictionary of strings) Table(s) of results grouped by the 'group_by' parameter
        """

        images = self._image_api[f"search_{query_preset}"](
            cloud_account, project_identifier, **kwargs
        )

        output = self._query_api.parse_and_output_table(
            cloud_account, images, "image", properties_to_select, group_by, get_html
        )

        return output

    def find_non_existent_images(self, cloud_account: str, project_identifier: str):
        """
        Returns a dictionary containing the ids of projects along with a list of non-existent images found within them
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A dictionary containing the non-existent server ids and their projects
        """
        return self._image_api.find_non_existent_images(
            cloud_account=cloud_account, project_identifier=project_identifier
        )

    def find_non_existent_projects(self, cloud_account: str):
        """
        Returns a dictionary containing the ids of non-existent projects along with a list of images that
        refer to them
        :param cloud_account: The associated clouds.yaml account
        :return: A dictionary containing the non-existent server ids and their projects
        """
        return self._image_api.find_non_existent_projects(cloud_account=cloud_account)
