from unittest.mock import create_autospec, NonCallableMock
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

    def test_floating_ip_get_found(self):
        """
        Tests the found FloatingIP is returned by get
        """
        cloud, ip = NonCallableMock(), NonCallableMock()
        returned = self.action.floating_ip_get(cloud, ip)

        self.network_mock.get_floating_ip.assert_called_once_with(cloud, ip)
        expected = self.network_mock.get_floating_ip.return_value
        assert returned == (True, expected)

    def test_floating_ip_get_not_found(self):
        """
        Tests an False status and error string are returned by get
        """
        self.network_mock.get_floating_ip.return_value = None
        returned = self.action.floating_ip_get(NonCallableMock(), NonCallableMock())
        assert returned[0] is False
        assert "could not be found" in returned[1]

    def test_list(self):
        """
        Tests the action returns the found floating ips
        """
        for query_preset in OpenstackFloatingIP.SEARCH_QUERY_PRESETS:
            self.action.floating_ip_list(
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
            self.floating_ip_mock[f"search_{query_preset}"].assert_called_once()
