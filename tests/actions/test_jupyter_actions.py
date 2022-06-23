from unittest.mock import create_autospec, Mock, NonCallableMock

from jupyter_api.user_api import UserApi
from src.jupyter import Jupyter
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestJupyterActions(OpenstackActionTestBase):
    """
    Unit tests for the Jupyter.* actions
    """

    action_cls = Jupyter

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.user_mock: UserApi = create_autospec(UserApi)
        config = {"user_api": self.user_mock}
        self.action: Jupyter = self.get_action_instance(config=config)

    def test_user_delete(self):
        """
        Tests the action deletes the list of users
        """
        endpoint = NonCallableMock()
        users = [NonCallableMock(), NonCallableMock()]

        self.action.action_service.get_value = Mock()
        self.action.user_delete(endpoint, users)

        # Should use dev token if unsure
        self.action.action_service.get_value.assert_called_once_with(
            "jupyter.dev_token", local=False, decrypt=True
        )
        token = self.action.action_service.get_value.return_value
        self.user_mock.delete_users(endpoint=endpoint, auth_token=token, users=users)

    def test_user_delete_prod(self):
        """
        Tests the action deletes the list of users using the prod token
        """
        endpoint = "prod"
        users = [NonCallableMock(), NonCallableMock()]

        self.action.action_service.get_value = Mock()
        self.action.user_delete(endpoint, users)

        # Should use dev token if unsure
        self.action.action_service.get_value.assert_called_once_with(
            "jupyter.prod_token", local=False, decrypt=True
        )
        token = self.action.action_service.get_value.return_value
        self.user_mock.delete_users(endpoint=endpoint, auth_token=token, users=users)
