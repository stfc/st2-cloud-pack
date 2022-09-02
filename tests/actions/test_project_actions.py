from unittest.mock import create_autospec, NonCallableMock

from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_project import OpenstackProject
from openstack_api.openstack_query import OpenstackQuery
from src.project_actions import ProjectAction
from structs.project_details import ProjectDetails
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestProjectAction(OpenstackActionTestBase):
    """
    Unit tests the Project.* actions
    """

    action_cls = ProjectAction

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Initialises the API mock used in the unit tests
        """
        super().setUp()
        self.identity_mock = create_autospec(OpenstackIdentity)
        self.project_mock = create_autospec(OpenstackProject)
        # Want to keep __getitem__ otherwise all f"search_{query_preset}"
        # calls will go to the same mock
        self.project_mock.__getitem__ = OpenstackProject.__getitem__

        self.query_mock = create_autospec(OpenstackQuery)
        self.action: ProjectAction = self.get_action_instance(
            api_mocks={
                "openstack_identity_api": self.identity_mock,
                "openstack_project_api": self.project_mock,
                "openstack_query_api": self.query_mock,
            }
        )

    def test_project_action_can_be_instantiated(self):
        """
        Tests the action can be instantiated without errors
        """
        action = self.get_action_instance()
        assert action

    def test_create_project_when_successful(self):
        """
        Tests that create project forwards the result when successful
        """
        expected_proj_params = {
            i: NonCallableMock()
            for i in ["name", "description", "is_enabled", "immutable"]
        }
        expected_proj_params.update({"email": "Test@Test.com"})

        # Check that default gets hard-coded in too
        packaged_proj = ProjectDetails(**expected_proj_params)

        returned_values = self.action.project_create(
            cloud_account="foo", **expected_proj_params
        )
        self.identity_mock.create_project.assert_called_once_with(
            cloud_account="foo", project_details=packaged_proj
        )

        assert returned_values[0] is True
        assert returned_values[1] == self.identity_mock.create_project.return_value

    def test_project_create_when_failed(self):
        """
        Tests that create project returns None and an error
        when the domain is not found
        """
        self.identity_mock.create_project.return_value = None

        returned_values = self.action.project_create(
            *{NonCallableMock() for _ in range(6)}
        )
        assert returned_values[0] is False
        assert returned_values[1] is None

    def test_project_delete_success(self):
        """
        Tests that on successful deletion it returns the correct status and string
        """
        self.identity_mock.delete_project.return_value = True
        returned_values = self.action.project_delete(
            NonCallableMock(), NonCallableMock()
        )
        assert returned_values == (True, "")

    def test_project_find_success(self):
        """
        Tests that the correct results are given for a found project
        """
        expected = NonCallableMock()
        self.identity_mock.find_project.return_value = expected
        returned_values = self.action.project_find(NonCallableMock(), NonCallableMock())
        assert returned_values == (True, expected)

    def test_project_find_failure(self):
        """
        Tests that the correct return is given when a project is not found
        """
        self.identity_mock.find_project.return_value = None
        returned_values = self.action.project_find(NonCallableMock(), NonCallableMock())
        assert returned_values[0] is False
        assert "could not be found" in returned_values[1]

    def test_update_project(self):
        """
        Tests that update project forwards the result when successful
        """
        expected_proj_params = {
            i: NonCallableMock()
            for i in ["name", "description", "is_enabled", "immutable"]
        }
        expected_proj_params.update({"email": "Test@Test.com"})

        # Check that default gets hard-coded in too
        packaged_proj = ProjectDetails(**expected_proj_params)

        # Ensure is_enabled is assigned if specefied
        for value in ["unchanged", "true", "false"]:
            expected_proj_params["is_enabled"] = value
            expected_proj_params["immutable"] = value
            packaged_proj.is_enabled = None if value == "unchanged" else value == "true"
            packaged_proj.immutable = None if value == "unchanged" else value == "true"

            returned_values = self.action.project_update(
                cloud_account="foo", project_identifier="bar", **expected_proj_params
            )
            self.identity_mock.update_project.assert_called_with(
                cloud_account="foo",
                project_identifier="bar",
                project_details=packaged_proj,
            )

            assert returned_values[0] is True
            assert returned_values[1] == self.identity_mock.update_project.return_value

    def test_run_dispatch(self):
        """
        Tests that dynamic dispatch works for all the expected methods
        """
        self._test_run_dynamic_dispatch(
            [
                "project_create",
                "project_delete",
                "project_find",
                "project_list",
                "project_update",
            ]
        )

    def test_project_list(self):
        """
        Tests the action returns the found projects
        """
        for query_preset in OpenstackProject.SEARCH_QUERY_PRESETS:
            self.action.project_list(
                cloud_account=NonCallableMock(),
                query_preset=query_preset,
                properties_to_select=NonCallableMock(),
                group_by=NonCallableMock(),
                get_html=NonCallableMock(),
                days=60,
                ids=NonCallableMock(),
                names=NonCallableMock(),
                name_snippets=NonCallableMock(),
                description_snippets=NonCallableMock(),
            )
            self.project_mock[f"search_{query_preset}"].assert_called_once()
