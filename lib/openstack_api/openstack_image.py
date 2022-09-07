from typing import List

from openstack.image.v2.image import Image

from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_query import OpenstackQuery
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from structs.email_params import EmailParams
from structs.email_query_params import EmailQueryParams
from structs.smtp_account import SMTPAccount


class OpenstackImage(OpenstackWrapperBase):
    # Lists all possible query presets for image.list
    SEARCH_QUERY_PRESETS: List[str] = [
        "all_images",
        "images_older_than",
        "images_younger_than",
        "images_last_updated_before",
        "images_last_updated_after",
        "images_id_in",
        "images_id_not_in",
        "images_name_in",
        "images_name_not_in",
        "images_name_contains",
        "images_name_not_contains",
        "images_non_existent_project",
    ]

    # Lists possible queries presets that don't require a project to function
    SEARCH_QUERY_PRESETS_NO_PROJECT: List[str] = [
        "images_older_than",
        "images_last_updated_before",
        "images_non_existent_project",
    ]

    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(self._connection_cls)
        self._query_api = OpenstackQuery(self._connection_cls)

    # Queries to be used for OpenstackQuery
    def _query_non_existent_project(self, cloud_account: str):
        """
        Returns a query that returns true when an image has a non-existent project
        """
        return (
            lambda a: self._identity_api.find_project(cloud_account, a["owner"]) is None
        )

    def __getitem__(self, item):
        return getattr(self, item)

    def search_all_images(
        self, cloud_account: str, project_identifier: str, **_
    ) -> List[Image]:
        """
        Returns a list of images matching a given query
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :return: A list of all images
        """
        filters = {"limit": 10000}
        if project_identifier != "":
            # list_images can only take project ids in the filters, not names so workaround
            project = self._identity_api.find_mandatory_project(
                cloud_account=cloud_account, project_identifier=project_identifier
            )
            filters.update({"owner": project["id"]})

        with self._connection_cls(cloud_account) as conn:
            return conn.image.images(**filters)

    def search_images_older_than(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[Image]:
        """
        Returns a list of images older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :param days: The number of days the images should be older than
        :return: A list of images matching the query
        """
        selected_images = self.search_all_images(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_images,
            self._query_api.query_datetime_before("created_at", days),
        )

    def search_images_younger_than(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[Image]:
        """
        Returns a list of images older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :param days: The number of days the images should be older than
        :return: A list of images matching the query
        """
        selected_images = self.search_all_images(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_images,
            self._query_api.query_datetime_after("created_at", days),
        )

    def search_images_last_updated_before(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[Image]:
        """
        Returns a list of images updated before a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :param days: The number of days before which the images should have last been updated
        :return: A list of images matching the query
        """
        selected_images = self.search_all_images(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_images,
            self._query_api.query_datetime_before("updated_at", days),
        )

    def search_images_last_updated_after(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[Image]:
        """
        Returns a list of images updated after a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :param days: The number of days after which the images should have last been updated
        :return: A list of images matching the query
        """
        selected_images = self.search_all_images(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_images,
            self._query_api.query_datetime_after("updated_at", days),
        )

    def search_images_name_in(
        self, cloud_account: str, project_identifier: str, names: List[str], **_
    ) -> List[Image]:
        """
        Returns a list of images with names in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :param names: List of names that should pass the query
        :return: A list of images matching the query
        """
        selected_images = self.search_all_images(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_images, self._query_api.query_prop_in("name", names)
        )

    def search_images_name_not_in(
        self, cloud_account: str, project_identifier: str, names: List[str], **_
    ) -> List[Image]:
        """
        Returns a list of images with names that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :param names: List of names that should not pass the query
        :return: A list of images matching the query
        """
        selected_images = self.search_all_images(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_images,
            self._query_api.query_prop_not_in("name", names),
        )

    def search_images_name_contains(
        self, cloud_account: str, project_identifier: str, name_snippets: List[str], **_
    ) -> List[Image]:
        """
        Returns a list of images with names containing the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :param name_snippets: List of name snippets that should be in the image names returned
        :return: A list of images matching the query
        """
        selected_images = self.search_all_images(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_images,
            self._query_api.query_prop_contains("name", name_snippets),
        )

    def search_images_name_not_contains(
        self, cloud_account: str, project_identifier: str, name_snippets: List[str], **_
    ) -> List[Image]:
        """
        Returns a list of images with names that don't contain the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :param name_snippets: List of name snippets that should not be in the image names returned
        :return: A list of images matching the query
        """
        selected_images = self.search_all_images(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_images,
            self._query_api.query_prop_not_contains("name", name_snippets),
        )

    def search_images_id_in(
        self, cloud_account: str, project_identifier: str, ids: List[str], **_
    ) -> List[Image]:
        """
        Returns a list of images with ids in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :param ids: List of ids that should pass the query
        :return: A list of images matching the query
        """
        selected_images = self.search_all_images(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_images, self._query_api.query_prop_in("id", ids)
        )

    def search_images_id_not_in(
        self, cloud_account: str, project_identifier: str, ids: List[str], **_
    ) -> List[Image]:
        """
        Returns a list of images with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :param ids: List of ids that should not pass the query
        :return: A list of images matching the query
        """
        selected_images = self.search_all_images(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_images, self._query_api.query_prop_not_in("id", ids)
        )

    def search_images_non_existent_project(
        self, cloud_account: str, project_identifier: str, **_
    ) -> List[Image]:
        """
        Returns a list of images with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated images with, can be empty for all projects
        :return: A list of images matching the query
        """
        selected_images = self.search_all_images(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_images, self._query_non_existent_project(cloud_account)
        )

    def email_users(
        self,
        cloud_account: str,
        smtp_account: SMTPAccount,
        project_identifier: str,
        query_preset: str,
        message: str,
        properties_to_select: List[str],
        email_params: EmailParams,
        **kwargs,
    ):
        """
        Finds all images matching a query and then sends emails to their project's contact email
        :param: smtp_account (SMTPAccount): SMTP config
        :param: cloud_account: The account from the clouds configuration to use
        :param: project_identifier: The project this applies to (or empty for all projects)
        :param: query_preset: The query to use when searching for images
        :param: message: Message to add to the body of emails sent
        :param: properties_to_select: The list of properties to select and output from the found images
        :param: email_params: See EmailParams
        :return:
        """
        query_params = EmailQueryParams(
            required_email_property="project_email",
            valid_search_queries=OpenstackImage.SEARCH_QUERY_PRESETS,
            valid_search_queries_no_project=OpenstackImage.SEARCH_QUERY_PRESETS_NO_PROJECT,
            search_api=self,
            object_type="image",
        )

        return self._query_api.email_users(
            cloud_account=cloud_account,
            smtp_account=smtp_account,
            query_params=query_params,
            project_identifier=project_identifier,
            query_preset=query_preset,
            message=message,
            properties_to_select=properties_to_select,
            email_params=email_params,
            **kwargs,
        )
