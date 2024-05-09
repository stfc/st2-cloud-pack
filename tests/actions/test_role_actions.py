from unittest.mock import create_autospec, NonCallableMock

from enums.user_domains import UserDomains
from openstack_api.openstack_roles import OpenstackRoles
from src.role_actions import RoleActions
from structs.role_details import RoleDetails
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestRoleActions(OpenstackActionTestBase):
    """
    Unit tests for the SecurityGroup.* actions
    """

    action_cls = RoleActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Initialises the action and injects mocks required for testing
        """
        super().setUp()
        self.role_mock = create_autospec(OpenstackRoles)
        self.action: RoleActions = self.get_action_instance(api_mocks=self.role_mock)

    def test_role_add(self):
        """
        Tests that role add forwards to the correct API
        """
        cloud = NonCallableMock()
        user, project, role = NonCallableMock(), NonCallableMock(), NonCallableMock()
        self.action.role_add(cloud, user, project, role, user_domain="StFC")
        expected_details = RoleDetails(
            user_identifier=user,
            user_domain=UserDomains.STFC,
            project_identifier=project,
            role_identifier=role,
        )
        self.role_mock.assign_role_to_user.assert_called_once_with(
            cloud_account=cloud, details=expected_details
        )

    def test_role_remove(self):
        """
        Tests that role removal forwards to the correct API
        """
        cloud = NonCallableMock()
        role, project = NonCallableMock(), NonCallableMock()
        domain, user = "stfc", NonCallableMock()
        self.action.role_remove(cloud, user, project, role, domain)
        expected_details = RoleDetails(
            user_identifier=user,
            user_domain=UserDomains.STFC,
            project_identifier=project,
            role_identifier=role,
        )
        self.role_mock.remove_role_from_user.assert_called_once_with(
            cloud_account=cloud, details=expected_details
        )
