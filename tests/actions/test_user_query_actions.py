from unittest.mock import patch, NonCallableMock
from parameterized import parameterized
from enums.cloud_domains import CloudDomains

from src.user_query_actions import UserQueryActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestServerQueryActions(OpenstackActionTestBase):
    """
    Unit tests for server.search.* actions
    """

    action_cls = UserQueryActions

    # pylint: disable=invalid-name
    def setUp(self):
        super().setUp()
        self.action: UserQueryActions = self.get_action_instance()
        self.mock_cloud_account = "dev"
        self.args = {
            "properties_to_select": ["user_id", "user_name"],
            "output_type": "to_str",
            "kwarg1": NonCallableMock(),
            "kwarg2": NonCallableMock(),
        }

    @parameterized.expand(
        [
            "search_all",
            "search_by_property",
            "search_by_regex",
        ]
    )
    @patch("src.user_query_actions.UserManager")
    def test_run(self, method_name, mock_user_manager):
        """
        Tests that run method can dispatch to UserManager methods
        """
        assert hasattr(mock_user_manager, method_name)
        mock_method = getattr(mock_user_manager.return_value, method_name)
        self.action.run(
            submodule=method_name, cloud_account=self.mock_cloud_account, **self.args
        )
        mock_user_manager.assert_called_once_with(cloud_account=CloudDomains.DEV)
        mock_method.assert_called_once_with(**self.args)
