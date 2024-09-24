from unittest.mock import patch, NonCallableMock, MagicMock
from importlib import import_module
import pytest

from src.openstack_actions import OpenstackActions
from tests.actions.openstack_action_test_base import OpenstackActionTestBase


@pytest.mark.parametrize("action_name", ["send_decom_flavor_email", "send_test_email"])
def test_module_exists(action_name):
    """
    Test that each action's entry-point module exists
    """
    workflow_module = import_module("workflows")

    assert hasattr(workflow_module, action_name)


class TestOpenstackActions(OpenstackActionTestBase):
    """
    Unit tests for actions that use workflow modules
    """

    action_cls = OpenstackActions
    # pylint: disable=invalid-name

    def setUp(self):
        """setup for tests"""
        super().setUp()
        self.action: OpenstackActions = self.get_action_instance()
        self.mock_kwargs = {
            "kwarg1": NonCallableMock(),
            "kwarg2": NonCallableMock(),
        }

    @patch("src.openstack_actions.import_module")
    def test_run(self, mock_import):
        """
        Tests that run method can dispatch to workflow methods
        """
        mock_action_module_name = "workflow.submodule.module.fn1"
        with patch.object(self.action, "parse_configs") as mock_parse_configs:
            self.action.run(
                lib_entry_point=mock_action_module_name,
                **self.mock_kwargs,
            )

        mock_parse_configs.assert_called_once_with(**self.mock_kwargs)
        mock_import.assert_called_once_with("workflow.submodule.module")
        mock_import.return_value.fn1.assert_called_once_with(
            **mock_parse_configs.return_value
        )

    @patch("src.openstack_actions.import_module")
    @patch("src.openstack_actions.OpenstackConnection")
    def test_run_with_openstack(self, mock_openstack_connection, mock_import):
        """
        Tests that run method can dispatch to workflow methods
        and sets up openstack connection when requires_openstack is True
        """
        mock_action_module_name = "workflow.submodule.module.fn1"
        mock_conn = MagicMock()
        mock_openstack_connection.return_value.__enter__.return_value = mock_conn

        with patch.object(self.action, "parse_configs") as mock_parse_configs:

            mock_parse_configs.return_value = {
                "kwarg1": "foo",
                "kwarg2": "bar",
                "cloud_account": "prod",
            }

            self.action.run(
                lib_entry_point=mock_action_module_name,
                requires_openstack=True,
                kwarg1="foo",
                kwarg2="bar",
                cloud_account="prod",
            )

        mock_openstack_connection.assert_called_once_with("prod")
        mock_parse_configs.assert_called_once_with(
            kwarg1="foo", kwarg2="bar", cloud_account="prod"
        )
        mock_import.assert_called_once_with("workflow.submodule.module")

        mock_import.return_value.fn1.assert_called_once_with(
            conn=mock_conn, kwarg1="foo", kwarg2="bar"
        )

    @patch("src.openstack_actions.SMTPAccount")
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
