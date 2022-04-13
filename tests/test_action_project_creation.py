from st2tests.actions import BaseActionTestCase
from actions.src.project import Project


class TestActionProject(BaseActionTestCase):
    action_cls = Project

    def test_project_creation(self):
        """
        Tests a project action can be instantiated
        """
        action = self.get_action_instance()
        assert action

    @staticmethod
    def test_stub():
        """
        Test stub to keep Pylint happy
        """
        assert True
