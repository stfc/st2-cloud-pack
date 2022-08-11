from unittest.mock import NonCallableMock, create_autospec

from free_ipa.freeipa_helpers import FreeIpaHelpers
from src.freeipa_action import FreeIpaAction

from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestFreeIpaActions(OpenstackActionTestBase):
    """
    Unit tests for the FreeIpa.* actions
    """

    action_cls = FreeIpaAction

    # pylint: disable=invalid-name
    def setUp(self):
        super().setUp()
        self.freeipa_helpers: FreeIpaHelpers = create_autospec(FreeIpaHelpers)
        config = {
            "freeipa_helpers": self.freeipa_helpers,
        }
        self.action: FreeIpaAction = self.get_action_instance(config=config)

    def test_generate_users(self):
        base_name, start_index, end_index = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        users = self.action.generate_users(base_name, start_index, end_index)
        self.freeipa_helpers.generate_users.assert_called_once_with(
            base_name, start_index, end_index
        )
        assert users == self.freeipa_helpers.generate_users.return_value

    def test_generate_password(self):
        num_passwords, num_chars = NonCallableMock(), NonCallableMock()
        password = self.action.generate_password(num_passwords, num_chars)
        self.freeipa_helpers.generate_password.assert_called_once_with(num_passwords, num_chars)
        assert password == self.freeipa_helpers.generate_password.return_value
