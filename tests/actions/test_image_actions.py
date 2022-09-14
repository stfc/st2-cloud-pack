from unittest.mock import call, create_autospec, NonCallableMock
from openstack_api.dataclasses import QueryParams
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
        Tests the action that lists images
        """
        calls = []
        for query_preset in OpenstackImage.SEARCH_QUERY_PRESETS:
            project_identifier = NonCallableMock()
            query_params = QueryParams(
                query_preset=query_preset,
                properties_to_select=NonCallableMock(),
                group_by=NonCallableMock(),
                get_html=NonCallableMock(),
            )
            extra_args = {
                "days": 60,
                "ids": None,
                "names": None,
                "name_snippets": None,
            }
            self.action.image_list(
                cloud_account="test",
                project_identifier=project_identifier,
                query_preset=query_preset,
                properties_to_select=query_params.properties_to_select,
                group_by=query_params.group_by,
                get_html=query_params.get_html,
                **extra_args
            )
            calls.append(
                call(
                    cloud_account="test",
                    query_params=query_params,
                    project_identifier=project_identifier,
                    **extra_args
                )
            )
        self.image_mock.search.assert_has_calls(calls)

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
