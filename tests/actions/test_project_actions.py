from unittest.mock import create_autospec, NonCallableMock

from openstack_api.openstack_identity import OpenstackIdentity
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
        # Want to keep __getitem__ otherwise all f"search_{query_preset}"
        # calls will go to the same mock

        self.action: ProjectAction = self.get_action_instance(
            api_mocks={
                "openstack_identity_api": self.identity_mock,
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
            for i in ["name", "description", "is_enabled", "immutable", "parent_id"]
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

    def test_create_project_when_parent_id_blank(self):
        """
        Tests that create project forwards the result when successful
        - when parent_id is blank, it passes parent_id = None
        """
        expected_proj_params = {
            i: NonCallableMock()
            for i in ["name", "description", "is_enabled", "immutable"]
        }
        expected_proj_params["parent_id"] = ""

        expected_proj_params.update({"email": "Test@Test.com"})

        # Check that default gets hard-coded in too
        packaged_proj = ProjectDetails(
            name=expected_proj_params["name"],
            description=expected_proj_params["description"],
            is_enabled=expected_proj_params["is_enabled"],
            immutable=expected_proj_params["immutable"],
            email="Test@Test.com",
            parent_id=None,
        )

        returned_values = self.action.project_create(
            cloud_account="foo",
            name=expected_proj_params["name"],
            description=expected_proj_params["description"],
            is_enabled=expected_proj_params["is_enabled"],
            immutable=expected_proj_params["immutable"],
            email="Test@Test.com",
            parent_id=None,
        )
        self.identity_mock.create_project.assert_called_once_with(
            cloud_account="foo", project_details=packaged_proj
        )

        assert returned_values[0] is True
        assert returned_values[1] == self.identity_mock.create_project.return_value

    def test_project_create_when_failed(self):
        """
        Tests that create project returns None and an error
        when the cloud domain is not found
        """
        self.identity_mock.create_project.return_value = None

        returned_values = self.action.project_create(
            *{NonCallableMock() for _ in range(7)}
        )
        assert returned_values[0] is False
        assert returned_values[1] is None

    def test_project_delete_success(self):
        """
        Tests that on successful deletion it returns the correct status and string
        """
        self.identity_mock.delete_project.return_value = True
        self.identity_mock.find_mandatory_project.return_value = NonCallableMock()
        returned_values = self.action.project_delete(
            cloud_account="test",
            project_identifier="ProjectID",
            delete=True,
        )
        self.identity_mock.find_mandatory_project.assert_called_once_with(
            cloud_account="test", project_identifier="ProjectID"
        )
        self.query_mock.parse_and_output_table.assert_called_once_with(
            items=[self.identity_mock.find_mandatory_project.return_value],
            property_funcs=self.project_mock.get_query_property_funcs.return_value,
            properties_to_select=["id", "name", "description", "email"],
            group_by="",
            return_html=False,
        )
        self.identity_mock.delete_project.assert_called_once_with(
            cloud_account="test", project_identifier="ProjectID"
        )
        self.assertEqual(
            returned_values,
            (
                True,
                f"The following project has been deleted:\n\n{self.query_mock.parse_and_output_table.return_value}",
            ),
        )

    def test_project_delete_safeguard(self):
        """
        Tests that project_delete does not delete when delete is False
        """
        self.identity_mock.delete_project.return_value = True
        self.identity_mock.find_mandatory_project.return_value = NonCallableMock()
        returned_values = self.action.project_delete(
            cloud_account="test",
            project_identifier="ProjectID",
            delete=False,
        )
        self.identity_mock.find_mandatory_project.assert_called_once_with(
            cloud_account="test", project_identifier="ProjectID"
        )
        self.query_mock.parse_and_output_table.assert_called_once_with(
            items=[self.identity_mock.find_mandatory_project.return_value],
            property_funcs=self.project_mock.get_query_property_funcs.return_value,
            properties_to_select=["id", "name", "description", "email"],
            group_by="",
            return_html=False,
        )
        self.identity_mock.delete_project.assert_not_called()
        self.assertEqual(
            returned_values,
            (
                False,
                (
                    f"Tick the delete checkbox to delete the project:"
                    f"\n\n{self.query_mock.parse_and_output_table.return_value}"
                ),
            ),
        )

    def test_run_dispatch(self):
        """
        Tests that dynamic dispatch works for all the expected methods
        """
        self._test_run_dynamic_dispatch(
            [
                "project_create",
                "project_delete",
            ]
        )
