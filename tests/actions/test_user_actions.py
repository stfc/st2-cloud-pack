from unittest.mock import call, create_autospec, NonCallableMock
from openstack_api.dataclasses import QueryParams
from openstack_api.openstack_user import OpenstackUser

from openstack_api.openstack_query import OpenstackQuery
from src.user_actions import UserActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestUserActions(OpenstackActionTestBase):
    """
    Unit tests for the User.* actions
    """

    action_cls = UserActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.user_mock = create_autospec(OpenstackUser)
        # Want to keep __getitem__ otherwise all f"search_{query_preset}"
        # calls will go to the same mock
        self.user_mock.__getitem__ = OpenstackUser.__getitem__

        self.query_mock = create_autospec(OpenstackQuery)
        self.action: UserActions = self.get_action_instance(
            api_mocks={
                "openstack_user_api": self.user_mock,
                "openstack_query_api": self.query_mock,
            }
        )

    def test_run_method(self):
        """
        Tests that run can dispatch to the Stackstorm facing methods
        """
        expected_methods = [
            "user_list",
        ]
        self._test_run_dynamic_dispatch(expected_methods)

    def test_list(self):
        """
        Tests the action that lists users
        """
        calls = []
        for query_preset in OpenstackUser.SEARCH_QUERY_PRESETS:
            project_identifier = NonCallableMock()
            query_params = QueryParams(
                query_preset=query_preset,
                properties_to_select=NonCallableMock(),
                group_by=NonCallableMock(),
                return_html=NonCallableMock(),
            )
            extra_args = {
                "ids": None,
                "names": None,
                "name_snippets": None,
            }
            self.action.user_list(
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
        self.user_mock.search.assert_has_calls(calls)
