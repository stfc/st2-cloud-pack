from unittest.mock import Mock, create_autospec, NonCallableMock

from openstack_api.openstack_server import OpenstackServer
from openstack_api.openstack_query import OpenstackQuery
from src.server_actions import ServerActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestServerActions(OpenstackActionTestBase):
    """
    Unit tests for the Server.* actions
    """

    action_cls = ServerActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.server_mock = create_autospec(OpenstackServer)

        # Want to keep mock of __getitem__ otherwise all f"search_{query_preset}"
        # calls will go to the same mock
        self.server_mock.__getitem__ = OpenstackServer.__getitem__

        self.query_mock = create_autospec(OpenstackQuery)
        self.action: ServerActions = self.get_action_instance(
            api_mock=self.server_mock,
            additional_mocks={"openstack_query_api": self.query_mock},
        )

    def test_list(self):
        """
        Tests the action returns the found Servers
        """
        query_presets = [
            "all_servers",
            "servers_older_than",
            "servers_younger_than",
            "servers_last_updated_before",
            "servers_last_updated_after",
            "servers_id_in",
            "servers_id_not_in",
            "servers_name_in",
            "servers_name_not_in",
            "servers_name_contains",
            "servers_name_not_contains",
            "servers_errored",
            "servers_shutoff",
            "servers_errored_and_shutoff",
        ]
        for query_preset in query_presets:
            self.action.server_list(
                NonCallableMock(),
                NonCallableMock(),
                query_preset,
                NonCallableMock(),
                NonCallableMock(),
                NonCallableMock(),
                days=60,
                ids=None,
                names=None,
                name_snippets=None,
            )
            self.server_mock[f"search_{query_preset}"].assert_called_once()

    def test_run_method(self):
        """
        Tests that run can dispatch to the Stackstorm facing methods
        """
        expected_methods = [
            "server_list",
        ]
        self._test_run_dynamic_dispatch(expected_methods)
