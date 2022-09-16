from unittest.mock import call, create_autospec, NonCallableMock
from openstack_api.dataclasses import QueryParams

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
        Tests the action that lists servers
        """
        calls = []
        for query_preset in OpenstackServer.SEARCH_QUERY_PRESETS:
            project_identifier = NonCallableMock()
            query_params = QueryParams(
                query_preset=query_preset,
                properties_to_select=NonCallableMock(),
                group_by=NonCallableMock(),
                return_html=NonCallableMock(),
            )
            extra_args = {
                "days": 60,
                "ids": None,
                "names": None,
                "name_snippets": None,
            }
            self.action.server_list(
                cloud_account="test",
                project_identifier=project_identifier,
                query_preset=query_preset,
                properties_to_select=query_params.properties_to_select,
                group_by=query_params.group_by,
                return_html=query_params.return_html,
                **extra_args
            )
            calls.append(
                call(
                    cloud_account="test",
                    query_params=query_params,
                    project_identifier=project_identifier,
                    **extra_args
                )
            )
        self.server_mock.search.assert_has_calls(calls)

    def test_find_non_existent_servers(self):
        """
        Tests that find_non_existent_servers works correctly
        """
        self.action.find_non_existent_servers("Cloud", "Project")
        self.server_mock.find_non_existent_servers.assert_called_once_with(
            cloud_account="Cloud", project_identifier="Project"
        )

    def test_find_non_existent_projects(self):
        """
        Tests that find_non_existent_projects works correctly
        """
        self.action.find_non_existent_projects("Cloud")
        self.server_mock.find_non_existent_projects.assert_called_once_with(
            cloud_account="Cloud"
        )

    def test_run_method(self):
        """
        Tests that run can dispatch to the Stackstorm facing methods
        """
        expected_methods = [
            "server_list",
            "find_non_existent_servers",
            "find_non_existent_projects",
        ]
        self._test_run_dynamic_dispatch(expected_methods)
