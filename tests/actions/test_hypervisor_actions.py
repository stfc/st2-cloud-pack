from unittest.mock import call, create_autospec, NonCallableMock
from openstack_api.dataclasses import QueryParams

from openstack_api.openstack_hypervisor import OpenstackHypervisor
from openstack_api.openstack_query import OpenstackQuery
from src.hypervisor_actions import HypervisorActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestHypervisorActions(OpenstackActionTestBase):
    """
    Unit tests for the Hypervisor.* actions
    """

    action_cls = HypervisorActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.hypervisor_mock = create_autospec(OpenstackHypervisor)
        # Want to keep __getitem__ otherwise all f"search_{query_preset}"
        # calls will go to the same mock
        self.hypervisor_mock.__getitem__ = OpenstackHypervisor.__getitem__

        self.query_mock = create_autospec(OpenstackQuery)
        self.action: HypervisorActions = self.get_action_instance(
            api_mocks={
                "openstack_hypervisor_api": self.hypervisor_mock,
                "openstack_query_api": self.query_mock,
            }
        )

    def test_run_method(self):
        """
        Tests that run can dispatch to the Stackstorm facing methods
        """
        expected_methods = [
            "hypervisor_list",
        ]
        self._test_run_dynamic_dispatch(expected_methods)

    def test_list(self):
        """
        Tests the action that lists hypervisors
        """
        calls = []
        for query_preset in OpenstackHypervisor.SEARCH_QUERY_PRESETS:
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
            self.action.hypervisor_list(
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
        self.hypervisor_mock.search.assert_has_calls(calls)
