from unittest.mock import create_autospec, NonCallableMock

from actions.src.project import Project
from openstack_wrappers.openstack_identity import OpenstackIdentity
from tests.openstack_action_test_case import OpenstackActionTestCase


class TestActionProject(OpenstackActionTestCase):
    action_cls = Project

    def test_project_can_be_instantiated(self):
        action = self.get_action_instance()
        assert action

    def test_find_domain_when_domain_found(self):
        expected = NonCallableMock()
        mock = create_autospec(OpenstackIdentity)
        mock.find_domain.return_value = expected

        action: Project = self.get_action_instance(api_mock=mock)
        returned_values = action.find_domain("foo")
        assert returned_values[0] is True
        assert returned_values[1] == expected
