import datetime
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

import openstack

from openstack_api.openstack_image import OpenstackImage


class OpenstackImageTests(unittest.TestCase):
    """
    Runs various tests to ensure we are using the Openstack
    Image module in the expected way
    """

    # pylint:disable=too-few-public-methods,invalid-name
    class MockProject:
        def __init__(self):
            self.id = "ProjectID"

        def __getitem__(self, item):
            return getattr(self, item)

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()
        with patch("openstack_api.openstack_image.OpenstackIdentity") as identity_mock:
            self.instance = OpenstackImage(self.mocked_connection)
            self.identity_module = identity_mock.return_value

        self.api = self.mocked_connection.return_value.__enter__.return_value

        self.mock_image_list = [
            {
                "id": "imageid1",
                "name": "ScientificLinux-6",
                "owner": "projectid1",
                "created_at": "2020-06-28T14:00:00Z",
                "updated_at": "2020-06-28T14:00:00Z",
            },
            {
                "id": "imageid2",
                "name": "ScientificLinux-7",
                "owner": "projectid1",
                "created_at": "2021-04-28T14:00:00Z",
                "updated_at": "2021-06-28T14:00:00Z",
            },
            {
                "id": "imageid3",
                "name": "Rocky Linux 8",
                "owner": "projectid2",
                "created_at": "2021-06-28T14:00:00Z",
                "updated_at": "2021-06-28T14:00:00Z",
            },
        ]

    def test_search_all_images_no_project(self):
        """
        Tests calling search_all_images with no project selected
        """
        self.instance.search_all_images(cloud_account="test", project_identifier="")

        self.mocked_connection.assert_called_once_with("test")

        self.api.image.images.assert_called_once_with(
            limit=10000,
        )

    def test_search_all_images(self):
        """
        Tests calling search_all_images
        """
        self.identity_module.find_mandatory_project.return_value = self.MockProject()
        self.instance.search_all_images(
            cloud_account="test", project_identifier="ProjectName"
        )

        self.mocked_connection.assert_called_once_with("test")

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud_account="test", project_identifier="ProjectName"
        )
        self.api.image.images.assert_called_once_with(
            owner="ProjectID",
            limit=10000,
        )

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_images_older_than(self, mock_datetime):
        """
        Tests calling search_images_older_than
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_images = MagicMock()
        self.instance.search_all_images.return_value = self.mock_image_list

        result = self.instance.search_images_older_than(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_image_list[0], self.mock_image_list[1]])

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_images_younger_than(self, mock_datetime):
        """
        Tests calling search_images_younger_than
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_images = MagicMock()
        self.instance.search_all_images.return_value = self.mock_image_list

        result = self.instance.search_images_younger_than(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_image_list[2]])

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_images_last_updated_before(self, mock_datetime):
        """
        Tests calling search_images_last_updated_before
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_images = MagicMock()
        self.instance.search_all_images.return_value = self.mock_image_list

        result = self.instance.search_images_last_updated_before(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_image_list[0]])

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_search_images_last_updated_after(self, mock_datetime):
        """
        Tests calling search_images_last_updated_after
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        self.instance.search_all_images = MagicMock()
        self.instance.search_all_images.return_value = self.mock_image_list

        result = self.instance.search_images_last_updated_after(
            cloud_account="test", project_identifier="", days=60
        )

        self.assertEqual(result, [self.mock_image_list[1], self.mock_image_list[2]])

    def test_search_images_name_in(self):
        """
        Tests calling search_images_name_in
        """

        self.instance.search_all_images = MagicMock()
        self.instance.search_all_images.return_value = self.mock_image_list

        result = self.instance.search_images_name_in(
            cloud_account="test",
            project_identifier="",
            names=["ScientificLinux-6", "ScientificLinux-7"],
        )

        self.assertEqual(result, [self.mock_image_list[0], self.mock_image_list[1]])

    def test_search_images_name_not_in(self):
        """
        Tests calling search_images_name_not_in
        """

        self.instance.search_all_images = MagicMock()
        self.instance.search_all_images.return_value = self.mock_image_list

        result = self.instance.search_images_name_not_in(
            cloud_account="test",
            project_identifier="",
            names=["ScientificLinux-6", "ScientificLinux-7"],
        )

        self.assertEqual(result, [self.mock_image_list[2]])

    def test_search_images_name_contains(self):
        """
        Tests calling search_images_name_contains
        """

        self.instance.search_all_images = MagicMock()
        self.instance.search_all_images.return_value = self.mock_image_list

        result = self.instance.search_images_name_contains(
            cloud_account="test",
            project_identifier="",
            name_snippets=["Scientific", "Linux"],
        )

        self.assertEqual(result, [self.mock_image_list[0], self.mock_image_list[1]])

        result = self.instance.search_images_name_contains(
            cloud_account="test", project_identifier="", name_snippets=["Rocky"]
        )

        self.assertEqual(result, [self.mock_image_list[2]])

        result = self.instance.search_images_name_contains(
            cloud_account="test", project_identifier="", name_snippets=["Linux"]
        )

        self.assertEqual(result, self.mock_image_list)

    def test_search_images_name_not_contains(self):
        """
        Tests calling search_images_name_not_contains
        """

        self.instance.search_all_images = MagicMock()
        self.instance.search_all_images.return_value = self.mock_image_list

        result = self.instance.search_images_name_not_contains(
            cloud_account="test",
            project_identifier="",
            name_snippets=["Scientific", "Linux"],
        )

        self.assertEqual(result, [])

        result = self.instance.search_images_name_not_contains(
            cloud_account="test", project_identifier="", name_snippets=["Rocky"]
        )

        self.assertEqual(result, [self.mock_image_list[0], self.mock_image_list[1]])

        result = self.instance.search_images_name_not_contains(
            cloud_account="test", project_identifier="", name_snippets=["Linux"]
        )

        self.assertEqual(result, [])

    def test_search_image_id_in(self):
        """
        Tests calling search_images_id_in
        """

        self.instance.search_all_images = MagicMock()
        self.instance.search_all_images.return_value = self.mock_image_list

        result = self.instance.search_images_id_in(
            cloud_account="test", project_identifier="", ids=["imageid1", "imageid2"]
        )

        self.assertEqual(result, [self.mock_image_list[0], self.mock_image_list[1]])

    def test_search_images_id_not_in(self):
        """
        Tests calling search_images_id_not_in
        """

        self.instance.search_all_images = MagicMock()
        self.instance.search_all_images.return_value = self.mock_image_list

        result = self.instance.search_images_id_not_in(
            cloud_account="test", project_identifier="", ids=["imageid1", "imageid2"]
        )

        self.assertEqual(result, [self.mock_image_list[2]])

    def test_search_images_non_existent_project(self):
        """
        Tests calling search_images_non_existent_project
        """

        self.instance.search_all_images = MagicMock()
        self.instance.search_all_images.return_value = self.mock_image_list

        self.identity_module.find_project.side_effect = [None, "Project", None]

        result = self.instance.search_images_non_existent_project(
            cloud_account="test", project_identifier=""
        )

        self.assertEqual(result, [self.mock_image_list[0], self.mock_image_list[2]])

    def test_find_non_existent_projects(self):
        """
        Tests calling find_non_existent_projects
        """
        # pylint:disable=too-few-public-methods,invalid-name,redefined-builtin
        class ObjectMock:
            def __init__(self, id):
                self.id = id
                self.owner = "Project"

        self.api.list_images.return_value = [
            ObjectMock("ImageID1"),
            ObjectMock("ImageID2"),
        ]
        self.api.identity.get_project.side_effect = (
            openstack.exceptions.ResourceNotFound()
        )

        result = self.instance.find_non_existent_projects(cloud_account="test")

        self.mocked_connection.assert_called_once_with("test")

        self.api.list_images.assert_called_once_with()

        self.assertEqual(
            result,
            {
                "Project": ["ImageID1", "ImageID2"],
            },
        )
