from unittest.mock import create_autospec, NonCallableMock
from openstack_api.openstack_image import OpenstackImage

from openstack_api.openstack_query import OpenstackQuery
from src.image_actions import ImageActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestImageActions(OpenstackActionTestBase):
    """
    Unit tests for the User.* actions
    """

    action_cls = ImageActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.image_mock = create_autospec(OpenstackImage)
        # Want to keep __getitem__ otherwise all f"search_{query_preset}"
        # calls will go to the same mock
        self.image_mock.__getitem__ = OpenstackImage.__getitem__

        self.query_mock = create_autospec(OpenstackQuery)
        self.action: ImageActions = self.get_action_instance(
            api_mocks={
                "openstack_image_api": self.image_mock,
                "openstack_query_api": self.query_mock,
            }
        )

    def test_run_method(self):
        """
        Tests that run can dispatch to the Stackstorm facing methods
        """
        expected_methods = [
            "image_list",
            "find_non_existent_images",
            "find_non_existent_projects",
        ]
        self._test_run_dynamic_dispatch(expected_methods)

    def test_list(self):
        """
        Tests the action returns the found floating ips
        """
        for query_preset in OpenstackImage.SEARCH_QUERY_PRESETS:
            self.action.image_list(
                cloud_account=NonCallableMock(),
                project_identifier=NonCallableMock(),
                query_preset=query_preset,
                properties_to_select=NonCallableMock(),
                group_by=NonCallableMock(),
                get_html=NonCallableMock(),
                days=60,
                ids=None,
                names=None,
                name_snippets=None,
            )
            self.image_mock[f"search_{query_preset}"].assert_called_once()

    def test_find_non_existent_images(self):
        """
        Tests that find_non_existent_images works correctly
        """
        self.action.find_non_existent_images("Cloud", "Project")
        self.image_mock.find_non_existent_images.assert_called_once_with(
            cloud_account="Cloud", project_identifier="Project"
        )

    def test_find_non_existent_projects(self):
        """
        Tests that find_non_existent_projects works correctly
        """
        self.action.find_non_existent_projects("Cloud")
        self.image_mock.find_non_existent_projects.assert_called_once_with(
            cloud_account="Cloud"
        )
