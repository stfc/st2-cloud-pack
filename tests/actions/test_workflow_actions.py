from unittest.mock import patch, NonCallableMock
import pytest

from src.workflow_actions import WorkflowActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


@pytest.mark.parametrize(
    "submodule_name, action_name", [("email", "send_decom_flavor_email")]
)
def test_submodules_exist(submodule_name, action_name):
    """
    Test that each submodule and action entry-points exist for each workflow action
    """
    workflow_module = __import__(f"workflows.{submodule_name}.{action_name}")
    assert hasattr(workflow_module, f"{submodule_name}")
    submodule = getattr(workflow_module, f"{submodule_name}")

    assert hasattr(submodule, action_name)
    action_module = getattr(submodule, action_name)

    assert hasattr(action_module, action_name)


class TestWorkflowActions(OpenstackActionTestBase):
    """
    Unit tests for actions that use workflow modules
    """

    action_cls = WorkflowActions
    # pylint: disable=invalid-name

    def setUp(self):
        """setup for tests"""
        super().setUp()
        self.action: WorkflowActions = self.get_action_instance()
        self.mock_kwargs = {
            "kwarg1": NonCallableMock(),
            "kwarg2": NonCallableMock(),
        }

    @patch("builtins.__import__")
    def test_run(self, mock_import):
        """
        Tests that run method can dispatch to workflow methods
        """

        mock_submodule_name = "submodule"
        mock_action_module_name = "action"

        with patch.object(self.action, "parse_configs") as mock_parse_configs:
            self.action.run(
                submodule_name=mock_submodule_name,
                action_name=mock_action_module_name,
                **self.mock_kwargs,
            )

        mock_parse_configs.assert_called_once_with(**self.mock_kwargs)
        mock_import.return_value.submodule.action.action.assert_called_once_with(
            **mock_parse_configs.return_value
        )

    @patch("src.workflow_actions.SMTPAccount")
    def parse_configs_with_smtp_account(self, mock_smtp_account):
        """
        tests that parse_configs parses smtp_account_name properly if provided
        """
        mock_smtp_account_name = NonCallableMock()
        res = self.action.parse_configs({"smtp_account_name": mock_smtp_account_name})
        mock_smtp_account.from_pack_config.assert_called_once_with(
            self.config, mock_smtp_account_name
        )
        assert res == {"smtp_account": mock_smtp_account.from_pack_config.return_value}

    def parse_configs_with_no_accounts(self):
        """
        tests that parse_configs doesn't do anything if no stackstorm config names given
        """
        mock_kwargs = {"arg1": "val1", "arg2": "val2"}
        res = self.action.parse_configs(mock_kwargs)
        assert res == mock_kwargs
