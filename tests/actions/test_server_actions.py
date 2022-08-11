from unittest.mock import create_autospec, NonCallableMock

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

        # Want to keep __getitem__ otherwise all f"search_{query_preset}"
        # calls will go to the same mock
        self.server_mock.__getitem__ = OpenstackServer.__getitem__

        self.query_mock = create_autospec(OpenstackQuery)
        self.action: ServerActions = self.get_action_instance(
            api_mocks={
                "openstack_server_api": self.server_mock,
                "openstack_query_api": self.query_mock,
            },
        )

    def test_list(self):
        """
        Tests the action returns the found Servers
        """
        for query_preset in OpenstackServer.SEARCH_QUERY_PRESETS:
            self.action.server_list(
                cloud_account=NonCallableMock(),
                project_identifier=NonCallableMock(),
                query_preset=query_preset,
                properties_to_select=NonCallableMock(),
                group_by=NonCallableMock(),
                get_html=NonCallableMock(),
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
