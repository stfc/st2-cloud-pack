from unittest.mock import call, create_autospec, NonCallableMock
from openstack_api.dataclasses import QueryParams

from openstack_api.openstack_floating_ip import OpenstackFloatingIP
from openstack_api.openstack_network import OpenstackNetwork
from openstack_api.openstack_query import OpenstackQuery
from src.floating_ip_actions import FloatingIPActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestFloatingIPActions(OpenstackActionTestBase):
    """
    Unit tests for the Network.* actions
    """

    action_cls = FloatingIPActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.network_mock = create_autospec(OpenstackNetwork)
        self.floating_ip_mock = create_autospec(OpenstackFloatingIP)
        # Want to keep __getitem__ otherwise all f"search_{query_preset}"
        # calls will go to the same mock
        self.floating_ip_mock.__getitem__ = OpenstackFloatingIP.__getitem__

        self.query_mock = create_autospec(OpenstackQuery)
        self.action: FloatingIPActions = self.get_action_instance(
            api_mocks={
                "openstack_network_api": self.network_mock,
                "openstack_floating_ip_api": self.floating_ip_mock,
                "openstack_query_api": self.query_mock,
            }
        )

    def test_run_method(self):
        """
        Tests that run can dispatch to the Stackstorm facing methods
        """
        expected_methods = [
            "floating_ip_get",
            "floating_ip_delete",
            "floating_ip_create",
            "floating_ip_list",
            "find_non_existent_floating_ips",
            "find_non_existent_projects",
        ]
        self._test_run_dynamic_dispatch(expected_methods)

    def test_allocate_floating_ip_empty(self):
        """
        Tests allocate floating IP if the list returned is empty
        """
        self.network_mock.allocate_floating_ips.return_value = []
        returned = self.action.floating_ip_create(
            NonCallableMock(), NonCallableMock(), NonCallableMock(), NonCallableMock()
        )
        assert returned == (False, [])

    def test_allocate_floating_ip_with_results(self):
        """
        Tests allocating floating IPs with a list will return the correct results
        """
        cloud, network = NonCallableMock(), NonCallableMock()
        project, num = NonCallableMock(), NonCallableMock()

        returned = self.action.floating_ip_create(cloud, network, project, num)
        self.network_mock.allocate_floating_ips.assert_called_once_with(
            cloud,
            network_identifier=network,
            project_identifier=project,
            number_to_create=num,
        )
        expected = self.network_mock.allocate_floating_ips.return_value
        assert returned == (True, expected)
