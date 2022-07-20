from unittest.mock import create_autospec, Mock, NonCallableMock

from nose.tools import raises
from parameterized import parameterized

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

    @parameterized.expand(["prod", "dev", "training"])
    def test_user_delete_gets_correct_key(self, endpoint):
        expected = f"jupyter.{endpoint}_token"

        users = [NonCallableMock(), NonCallableMock()]
        self.action.action_service.get_value = Mock()
        self.action.user_delete(endpoint, users)

        self.action.action_service.get_value.assert_called_once_with(
            expected, local=False, decrypt=True
        )
        token = self.action.action_service.get_value.return_value
        self.user_mock.delete_users.assert_called_once_with(
            endpoint=endpoint, auth_token=token, users=users
        )

    @raises(KeyError)
    def test_user_delete_throws_unknown_env(self):
        self.action.user_delete("unknown", NonCallableMock())
