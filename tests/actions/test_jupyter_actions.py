from unittest.mock import create_autospec, Mock, NonCallableMock, NonCallableMagicMock

from nose.tools import raises
from parameterized import parameterized

from jupyter_api.user_api import UserApi
from src.jupyter import Jupyter
from structs.jupyter_users import JupyterUsers
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
        self.jupyter_keys = NonCallableMagicMock()
        config = {"user_api": self.user_mock, "jupyter": self.jupyter_keys}
        self.action: Jupyter = self.get_action_instance(config=config)

    @parameterized.expand(["prod", "dev", "training"])
    def test_user_delete_gets_correct_key(self, endpoint):
        token = self.jupyter_keys[endpoint]

        users, start_index, end_index = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        expected = JupyterUsers(users, start_index, end_index)
        self.action.action_service.get_value = Mock()
        self.action.user_delete(endpoint, users, start_index, end_index)

        self.user_mock.delete_users.assert_called_once_with(
            endpoint=endpoint, auth_token=token, users=expected
        )

    @raises(KeyError)
    def test_user_delete_throws_unknown_env(self):
        self.action.user_delete("unknown", NonCallableMock())
