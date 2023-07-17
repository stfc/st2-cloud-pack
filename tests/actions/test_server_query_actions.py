from unittest.mock import patch, NonCallableMock, MagicMock
from parameterized import parameterized
from src.server_query_actions import ServerQueryActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase

from enums.query.query_output_types import QueryOutputTypes
from enums.cloud_domains import CloudDomains
from enums.query.props.server_properties import ServerProperties

from structs.query.query_output_details import QueryOutputDetails


class TestServerQueryActions(OpenstackActionTestBase):
    """
    Unit tests for server.search.* actions
    """

    action_cls = ServerQueryActions

    def setUp(self):
        super().setUp()
        self.action: ServerQueryActions = self.get_action_instance()
        self.args = {
            "cloud_account": "dev",
            "properties_to_select": ["server_id", "server_name"],
            "return_type": "to_str",
            "kwarg1": NonCallableMock(),
            "kwarg2": NonCallableMock(),
        }

    @parameterized.expand(
        [
            "search_all",
            "search_by_datetime",
            "search_by_property",
            "search_by_regex",
        ]
    )
    def test_run(self, method_name):
        """
        Tests that run method can dispatch to ServerManager methods
        """
        assert hasattr(self.action._server_manager, method_name)

        self.action._server_manager = MagicMock()
        mock_method = getattr(self.action._server_manager.return_value, method_name)

        self.action.run(submodule=method_name, **self.args)

        self.action._server_manager.assert_called_once_with(CloudDomains.DEV)
        mock_method.assert_called_once_with(
            output_details=QueryOutputDetails(
                properties_to_select=[
                    ServerProperties.SERVER_ID,
                    ServerProperties.SERVER_NAME,
                ],
                output_type=QueryOutputTypes.TO_STR,
            ),
            kwarg1=self.args["kwarg1"],
            kwarg2=self.args["kwarg2"],
        )
