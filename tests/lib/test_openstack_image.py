from dataclasses import dataclass
import datetime
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

import openstack

from openstack_api.openstack_image import OpenstackImage


# pylint:disable=too-many-public-methods


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
            self.search_query_presets = OpenstackImage.SEARCH_QUERY_PRESETS
            self.search_query_presets_no_project = (
                OpenstackImage.SEARCH_QUERY_PRESETS_NO_PROJECT
            )

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

    def test_property_funcs(self):
        """
        Tests calling get_query_property_funcs
        """

        class _ImageMock:
            owner: str

            def __init__(self, owner: str):
                self.owner = owner

            def __getitem__(self, attr):
                return getattr(self, attr)

        item = _ImageMock("Owner")
        property_funcs = self.instance.get_query_property_funcs("test")

        # Test project_name
        result = property_funcs["project_name"](item)
        self.assertEqual(result, self.api.identity.find_project.return_value["name"])

        # Test project_email
        result = property_funcs["project_email"](item)
        self.assertEqual(result, self.identity_module.find_project_email.return_value)

    def test_search_all_images_no_project(self):
        """
        Tests calling search_all_images with no project selected
        """
        self.instance.search_all_images(cloud_account="test", project_identifier="")

        self.mocked_connection.assert_called_once_with("test")

        self.api.image.images.assert_called_once_with()

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

    def test_find_non_existent_images(self):
        """
        Tests calling find_non_existent_images
        """

        @dataclass
        class _ObjectMock:
            # pylint: disable=invalid-name
            id: str
            owner: str

            def __getitem__(self, item):
                return getattr(self, item)

        self.api.image.images.return_value = [
            _ObjectMock("ObjectID1", "ProjectID1"),
            _ObjectMock("ObjectID2", "ProjectID1"),
            _ObjectMock("ObjectID3", "ProjectID1"),
        ]

        self.api.image.get_image.side_effect = [
            openstack.exceptions.ResourceNotFound(),
            openstack.exceptions.ResourceNotFound(),
            "",
        ]

        result = self.instance.find_non_existent_images(
            cloud_account="test", project_identifier="project"
        )

        self.assertEqual(
            result,
            {
                self.api.identity.find_project.return_value.id: [
                    "ObjectID1",
                    "ObjectID2",
                ]
            },
        )

    def test_find_non_existent_projects(self):
        """
        Tests calling find_non_existent_projects
        """

        @dataclass
        class _ObjectMock:
            # pylint: disable=invalid-name
            id: str
            owner: str

            def __getitem__(self, item):
                return getattr(self, item)

        self.api.list_images.return_value = [
            _ObjectMock("ImageID1", "ProjectID1"),
            _ObjectMock("ImageID2", "ProjectID1"),
            _ObjectMock("ImageID3", "ProjectID2"),
        ]

        self.api.identity.get_project.side_effect = [
            openstack.exceptions.ResourceNotFound(),
            openstack.exceptions.ResourceNotFound(),
            "",
        ]

        result = self.instance.find_non_existent_projects(cloud_account="test")

        self.assertEqual(result, {"ProjectID1": ["ImageID1", "ImageID2"]})
