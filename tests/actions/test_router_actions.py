from unittest.mock import create_autospec, NonCallableMock

from openstack_api.openstack_network import OpenstackNetwork
from src.router_actions import RouterActions
from structs.router_details import RouterDetails
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestRouterActions(OpenstackActionTestBase):
    """
    Unit tests for the Network.* actions
    """

    action_cls = RouterActions

    # pylint: disable=invalid-name
    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.network_mock = create_autospec(OpenstackNetwork)
        self.action: RouterActions = self.get_action_instance(
            api_mock=self.network_mock
        )

    def test_router_create(self):
        """
        Tests creating a router makes the correct call
        """
        cloud, project = NonCallableMock(), NonCallableMock()
        name, description = NonCallableMock(), NonCallableMock()
        gateway, distributed, ha = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        returned = self.action.router_create(
            cloud,
            project_identifier=project,
            router_name=name,
            router_description=description,
            external_gateway=gateway,
            is_distributed=distributed,
            is_ha=ha,
        )

        self.network_mock.create_router.assert_called_once_with(
            cloud, RouterDetails(project, name, description, gateway, distributed, ha)
        )
        expected = self.network_mock.create_router.return_value
        assert returned == (True, expected)

    def test_find_router_found(self):
        """
        Tests that find router returns the correct result when found
        """
        cloud, project, router = NonCallableMock(), NonCallableMock(), NonCallableMock()
        returned = self.action.router_get(cloud, project, router)
        self.network_mock.get_router.assert_called_once_with(cloud, project, router)
        assert returned == (True, self.network_mock.get_router.return_value)

    def test_find_router_not_found(self):
        """
        Tests that find router returns the correct result if nothing is found
        """
        self.network_mock.get_router.return_value = None
        returned = self.action.router_get(
            NonCallableMock(), NonCallableMock(), NonCallableMock()
        )
        assert returned[0] is False
        assert "router could not be found" in returned[1]

    def test_add_interface_to_router(self):
        """
        Tests that add interface to router makes the correct call
        """
        cloud, project = NonCallableMock(), NonCallableMock()
        router, subnet = NonCallableMock(), NonCallableMock()

        returned = self.action.router_add_interface(cloud, project, router, subnet)
        self.network_mock.add_interface_to_router.assert_called_once_with(
            cloud, project, router, subnet
        )
        assert returned == (
            True,
            self.network_mock.add_interface_to_router.return_value,
        )
