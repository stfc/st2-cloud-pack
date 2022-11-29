from unittest.mock import create_autospec, NonCallableMock

from openstack_api.openstack_flavor import OpenstackFlavor
from src.flavor_actions import FlavorActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestFlavorActions(OpenstackActionTestBase):
    """
    Unit tests for Flavor.* actions
    """

    action_cls = FlavorActions

    # pylint: disable=invalid-name

    def setUp(self):
        """
        Prepares the mock API and injects it into a new instance
        """
        super().setUp()
        self.flavor_mock = create_autospec(OpenstackFlavor)
        self.action: FlavorActions = self.get_action_instance(
            api_mocks={"openstack_flavor_api": self.flavor_mock}
        )

    def test_run_method(self):
        """
        Tests that run can dispatch to the Stackstorm facing methods
        """
        expected_methods = [
            "list_missing_flavors",
        ]
        self._test_run_dynamic_dispatch(expected_methods)

    def test_migrate_flavors(self):
        """
        Tests the action that lists missing flavors (if any)
        """
        source_cloud, dest_cloud = NonCallableMock(), NonCallableMock()
        returned = self.action.list_missing_flavors(
            source_cloud=source_cloud, dest_cloud=dest_cloud
        )
        assert returned == self.flavor_mock.migrate_flavors.return_value
        self.flavor_mock.migrate_flavors.assert_called_once_with(
            source_cloud=source_cloud, dest_cloud=dest_cloud
        )
