from unittest.mock import patch, NonCallableMock

from src.email_actions import ST2EmailActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


class TestST2EmailActions(OpenstackActionTestBase):
    """
    Unit tests for email.* actions
    """

    action_cls = ST2EmailActions
    # pylint: disable=invalid-name

    def setUp(self):
        """setup for tests"""
        super().setUp()
        self.action: ST2EmailActions = self.get_action_instance()
        self.mock_kwargs = {
            "kwarg1": NonCallableMock(),
            "kwarg2": NonCallableMock(),
        }

    @patch("src.email_actions.EmailActions")
    @patch("src.email_actions.SMTPAccount")
    def test_run(self, mock_smtp_account, mock_email_actions):
        """
        Tests that run method can dispatch to EmailActions methods
        """
        method_name = "send_test_email"
        assert hasattr(mock_email_actions, method_name)
        mock_method = getattr(mock_email_actions.return_value, method_name)
        self.action.run(
            submodule=method_name, smtp_account_name="config1", **self.mock_kwargs
        )

        mock_smtp_account.from_pack_config.assert_called_once_with(
            self.action.config, "config1"
        )
        mock_email_actions.assert_called_once()
        mock_method.assert_called_once_with(
            smtp_account=mock_smtp_account.from_pack_config.return_value,
            **self.mock_kwargs
        )
