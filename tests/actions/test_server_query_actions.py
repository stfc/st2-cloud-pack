from unittest.mock import patch, NonCallableMock

from enums.cloud_domains import CloudDomains

from src.server_query_actions import ServerQueryActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestServerQueryActions(OpenstackActionTestBase):
    """
    Unit tests for server.search.* actions
    """

    action_cls = ServerQueryActions

    # pylint: disable=invalid-name
    def setUp(self):
        super().setUp()
        self.action: ServerQueryActions = self.get_action_instance()
        self.mock_cloud_account = "dev"
        self.args = {
            "properties_to_select": ["server_id", "server_name"],
            "output_type": "to_str",
            "kwarg1": NonCallableMock(),
            "kwarg2": NonCallableMock(),
        }

    @pytest.mark.parametrize("val",
        [
            "search_all",
            "search_by_datetime",
            "search_by_property",
            "search_by_regex",
        ]
    )
    @patch("src.server_query_actions.ServerManager")
    def test_run(self, method_name, mock_server_manager):
        """
        Tests that run method can dispatch to ServerManager methods
        """
        assert hasattr(mock_server_manager, method_name)
        mock_method = getattr(mock_server_manager.return_value, method_name)
        self.action.run(
            submodule=method_name, cloud_account=self.mock_cloud_account, **self.args
        )
        mock_server_manager.assert_called_once_with(cloud_account=CloudDomains.DEV)
        mock_method.assert_called_once_with(**self.args)
