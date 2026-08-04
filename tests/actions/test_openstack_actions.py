from unittest.mock import MagicMock, NonCallableMock, patch
import pytest
from src.openstack_actions import ACCOUNT_CONFIGS, OpenstackActions


@pytest.fixture(name="action")
def action_fixture():
    """OpenstackActions with a stubbed pack config and a silenced logger."""
    action = OpenstackActions(config={})
    action.logger = MagicMock()
    return action


@patch("src.openstack_actions.import_module")
def test_run_dispatches(mock_import, action):
    """Test action dispatch - test path is split into module and attribute correctly."""
    action_func = mock_import.return_value.fn1
    result = action.run(lib_entry_point="fake.module.fn1", foo="bar")
    mock_import.assert_called_once_with("fake.module")
    action_func.assert_called_once_with(foo="bar")
    assert result == action_func.return_value


@patch("src.openstack_actions.import_module")
def test_run_nested_module(mock_import, action):
    """Test action dispatch for deeply nested module."""
    action.run(lib_entry_point="a.b.c.d.fn2")
    mock_import.assert_called_once_with("a.b.c.d")
    mock_import.return_value.fn2.assert_called_once_with()


@patch("src.openstack_actions.import_module")
def test_run_dispatches_no_kwargs(mock_import, action):
    """Test action dispatch with no user-defined params."""
    action.run(lib_entry_point="fake.module.fn3")
    mock_import.return_value.fn3.assert_called_once_with()


def test_run_dispatch_fails_when_module_not_given(action):
    """Test action dispatch raises error where no module path provided."""
    with pytest.raises(ValueError):
        action.run(lib_entry_point="some_func")


@patch("src.openstack_actions.import_module")
def test_run_dispatch_fails_when_function_not_found(mock_import, action):
    """Test action raises error when function name doesn't exist in module spec."""
    mock_import.return_value = NonCallableMock(spec=[])

    with pytest.raises(AttributeError):
        action.run(lib_entry_point="fake.module.does_not_exist")


@patch("src.openstack_actions.import_module")
def test_run_parse_results_propagate(mock_import, action):
    """Test that whatever parse_configs returns reaches the lib function."""
    with patch.object(action, "parse_configs") as mock_parse:
        mock_parse.return_value = {"parsed": True}
        action.run(lib_entry_point="fake.module.fn1", raw="value")

    mock_parse.assert_called_once_with(raw="value")
    mock_import.return_value.fn1.assert_called_once_with(parsed=True)


@patch("src.openstack_actions.OpenstackConnection")
@patch("src.openstack_actions.import_module")
def test_run_parses_cloud_account_when_given(mock_import, mock_conn_cls, action):
    """when cloud_account is given, test that it is consumed and open connection passed as conn."""
    action_func = mock_import.return_value.fn1

    result = action.run(
        lib_entry_point="fake.module.fn1",
        cloud_account="dev",
        kwarg1="kept",
        kwarg2="kept",
    )

    mock_conn_cls.assert_called_once_with("dev")
    # equality on the full call also proves cloud_account was removed
    action_func.assert_called_once_with(
        conn=mock_conn_cls.return_value.__enter__.return_value,
        kwarg1="kept",
        kwarg2="kept",
    )
    assert result == action_func.return_value


@pytest.mark.parametrize(
    "name_key,obj_key,loader",
    [(key, val[0], val[1]) for key, val in ACCOUNT_CONFIGS.items()],
    ids=list(ACCOUNT_CONFIGS),
)
def test_parse_configs_parses_accounts(action, name_key, obj_key, loader):
    """Tests that parse_config converts each *_name key in ACCOUNT_CONFIGS into respective dataclasses"""
    with patch.object(loader, "from_pack_config") as mock_loader:
        result = action.parse_configs(**{name_key: "prod"})

    mock_loader.assert_called_once_with(action.config, "prod")
    # equality on the whole dict also proves the *_name key was removed
    assert result == {obj_key: mock_loader.return_value}


def test_parse_configs_parses_multiple_accounts(action):
    """Tests that parse_config converts multiple *_name keys in ACCOUNT_CONFIGS when given"""
    smtp_obj, smtp_cls = ACCOUNT_CONFIGS["smtp_account_name"]
    jira_obj, jira_cls = ACCOUNT_CONFIGS["jira_account_name"]

    with patch.object(smtp_cls, "from_pack_config") as mock_smtp:
        with patch.object(jira_cls, "from_pack_config") as mock_jira:
            result = action.parse_configs(
                smtp_account_name="default", jira_account_name="default"
            )

    assert result == {
        smtp_obj: mock_smtp.return_value,
        jira_obj: mock_jira.return_value,
    }


# ---------------------------------------------------------------------------
# parse_configs() - chatops
# ---------------------------------------------------------------------------
# TODO: REMOVE THIS AND USE A DATACLASS AND from_pack_config() LIKE ALL OTHERS


@pytest.fixture(name="chatops_action")
def chatops_action_fixture():
    action = OpenstackActions(
        config={
            "chatops_sensor": {
                "token": "a-token",
                "endpoint": "https://chat.example.com",
                "channel": "#alerts",
            }
        }
    )
    action.logger = MagicMock()
    return action


def test_parse_configs_parses_chatops_config(chatops_action):
    """Test that parse_config pulls relevant chatops data from pack config and returns it"""
    result = chatops_action.parse_configs(chatops_reminder_type="daily", extra=1)

    assert result == {
        "token": "a-token",
        "endpoint": "https://chat.example.com",
        "channel": "#alerts",
        "reminder_type": "daily",
        "extra": 1,
    }
