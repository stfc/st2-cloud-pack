import unittest
from unittest.mock import patch, NonCallableMock, Mock, create_autospec

from nose.tools import raises

from exceptions.item_not_found_error import ItemNotFoundError
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_roles import OpenstackRoles


class OpenstackRolesTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Sets up the various mocks required in this test
        """
        super().setUp()
        self.mocked_connection = create_autospec(OpenstackConnection)
        with patch("openstack_api.openstack_roles.OpenstackIdentity") as identity_mock:
            identity_mock.return_value = create_autospec(OpenstackIdentity)
            self.instance = OpenstackRoles(self.mocked_connection)
            self.identity_module = identity_mock.return_value

        self._api = self.mocked_connection.return_value.__enter__.return_value.identity

    @raises(ItemNotFoundError)
    def test_assign_roles_throws_missing_user(self):
        """
        Tests that an exception is thrown if the specified user is not found
        """
        self.identity_module.find_user.return_value = None
        self.instance.assign_role_to_user(NonCallableMock(), NonCallableMock())

    @raises(ItemNotFoundError)
    def test_assign_roles_throws_missing_role(self):
        """
        Tests that an exception is thrown if the specified role is not found
        """
        self.instance.find_role = Mock(return_value=None)
        self.instance.assign_role_to_user(NonCallableMock(), NonCallableMock())

    def test_assign_roles_makes_correct_call(self):
        """
        Tests that assign role forwards the found objects onto
        the assignment API
        """
        cloud = NonCallableMock()
        details = NonCallableMock()

        self.instance.find_role = Mock()
        self.instance.assign_role_to_user(cloud, details)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, details.project_identifier
        )
        self.identity_module.find_user.assert_called_once_with(
            cloud, details.user_identifier, details.user_domain
        )
        self.instance.find_role.assert_called_once_with(cloud, details.role_identifier)

        self._api.assign_project_role_to_user.assert_called_once_with(
            project=self.identity_module.find_mandatory_project.return_value,
            user=self.identity_module.find_user.return_value,
            role=self.instance.find_role.return_value,
        )

    @raises(MissingMandatoryParamError)
    def test_find_role_raises_missing(self):
        """
        Tests that an exception is thrown if an empty string is provided
        """
        self.instance.find_role(NonCallableMock(), " \t")

    def test_find_role_returns(self):
        """
        Tests find role calls the correct API and returns the result
        """
        cloud, role = NonCallableMock(), NonCallableMock()
        found = self.instance.find_role(cloud, role)

        self.mocked_connection.assert_called_once_with(cloud)
        self._api.find_role.assert_called_once_with(role.strip(), ignore_missing=True)
        expected = self._api.find_role.return_value
        assert found == expected

    @raises(ItemNotFoundError)
    def test_remove_role_throws_user_not_found(self):
        """
        Tests remove role throws if the user was not found
        """
        self.identity_module.find_user.return_value = None
        self.instance.remove_role_from_user(NonCallableMock(), NonCallableMock())

    @raises(ItemNotFoundError)
    def test_remove_role_throws_role_not_found(self):
        """
        Tests remove role throws if the role was not found
        """
        self.instance.find_role = Mock(return_value=None)
        self.instance.remove_role_from_user(NonCallableMock(), NonCallableMock())

    def test_remove_roles_makes_correct_call(self):
        """
        Tests that removal forwards the found objects onto
        the unassign API
        """
        cloud = NonCallableMock()
        details = NonCallableMock()

        self.instance.find_role = Mock()
        self.instance.remove_role_from_user(cloud, details)

        self.identity_module.find_mandatory_project.assert_called_once_with(
            cloud, details.project_identifier
        )
        self.identity_module.find_user.assert_called_once_with(
            cloud, details.user_identifier, details.user_domain
        )
        self.instance.find_role.assert_called_once_with(cloud, details.role_identifier)

        self._api.unassign_project_role_from_user.assert_called_once_with(
            project=self.identity_module.find_mandatory_project.return_value,
            user=self.identity_module.find_user.return_value,
            role=self.instance.find_role.return_value,
        )
