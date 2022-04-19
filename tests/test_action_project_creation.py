from unittest.mock import create_autospec, NonCallableMock

from actions.src.project import Project
from openstack_wrappers.openstack_identity import OpenstackIdentity
from tests.openstack_action_test_case import OpenstackActionTestCase


class TestActionProject(OpenstackActionTestCase):
    action_cls = Project

    def test_project_can_be_instantiated(self):
        """
        Tests the action can be instantiated without errors
        """
        action = self.get_action_instance()
        assert action

    def test_find_domain_when_domain_found(self):
        """
        Tests that find domain forwards the result as-is when a domain is found
        """
        expected = NonCallableMock()
        mock = create_autospec(OpenstackIdentity)
        mock.find_domain.return_value = expected

        action: Project = self.get_action_instance(api_mock=mock)
        returned_values = action.find_domain("account", "foo")
        assert returned_values[0] is True
        assert returned_values[1] == expected

    def test_find_domain_when_domain_not_found(self):
        """
        Tests that find domain returns None and an error
        when the domain is not found
        """
        mock = create_autospec(OpenstackIdentity)
        mock.find_domain.return_value = None

        action: Project = self.get_action_instance(api_mock=mock)
        returned_values = action.find_domain("account", "foo")
        assert returned_values[0] is False
        assert returned_values[1] is None
