from typing import Callable
from unittest.mock import NonCallableMock, Mock

from src.freeipa import FreeIpa
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestFreeIpaActions(OpenstackActionTestBase):
    """
    Unit tests for the FreeIpa.* actions
    """

    action_cls = FreeIpa

    # pylint: disable=invalid-name
    def setUp(self):
        super().setUp()
        self.password_generator: Callable = Mock()
        config = {"password_gen": self.password_generator}
        self.action: FreeIpa = self.get_action_instance(config=config)

    def test_generate_password(self):
        num_chars = NonCallableMock()
        password = self.action.generate_password(num_chars)
        self.password_generator.assert_called_once_with(num_chars)
        assert password == self.password_generator.return_value
