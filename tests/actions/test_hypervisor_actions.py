from unittest.mock import create_autospec, NonCallableMock

from openstack_api.openstack_hypervisor import OpenstackHypervisor
from src.hypervisor_actions import HypervisorActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestNetworkActions(OpenstackActionTestBase):
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
        self.hv_mock = create_autospec(OpenstackHypervisor)
        self.action: HypervisorActions = self.get_action_instance(
            api_mocks=self.hv_mock
        )

    def test_find_hv(self):
        """
        Tests the params and results get marshalled correctly
        """
        expected = NonCallableMock()
        params = NonCallableMock(), NonCallableMock()

        self.hv_mock.find_hypervisor.return_value = expected
        returned = self.action.find_hypervisor(
            cloud_account=params[0],
            search_type=params[1],
        )

        assert returned == expected
        self.hv_mock.find_hypervisor.assert_called_once_with(
            cloud_account=params[0], search_type=params[1]
        )

    def test_run_method(self):
        """
        Tests that run can dispatch to the Stackstorm facing methods
        """
        expected_methods = ["find_hypervisor"]
        self._test_run_dynamic_dispatch(expected_methods)
