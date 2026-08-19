from unittest.mock import MagicMock, NonCallableMock, patch
import pytest
from src.openstack_actions import ACCOUNT_CONFIGS, OpenstackActions


@pytest.fixture(name="action")
def action_fixture():
    """OpenstackActions with a stubbed pack config and a silenced logger."""
    action = OpenstackActions(config={})
    action.logger = MagicMock()
    return action


# pylint: disable=unused-argument
def simple_fn(a: int, b: int):
    return "success"


def simple_fn_no_kwargs():
    return "success_no_kwargs"


@patch("src.openstack_actions.import_module")
def test_run_dispatches(mock_import, action):
    """Test action dispatch - kwargs are passed through correctly"""
    mock_import.return_value.fn1 = simple_fn
    result = action.run(lib_entry_point="fake.module.fn1", a=0, b=1)
    mock_import.assert_called_once_with("fake.module")
    assert result == "success"


@patch("src.openstack_actions.import_module")
def test_run_nested_module(mock_import, action):
    """Test action dispatch for deeply nested module."""
    action.run(lib_entry_point="a.b.c.d.fn2")
    mock_import.assert_called_once_with("a.b.c.d")
    mock_import.return_value.fn2.assert_called_once_with()


@patch("src.openstack_actions.import_module")
def test_run_dispatches_no_kwargs(mock_import, action):
    """Test action dispatch with no user-defined params."""
    mock_import.return_value.fn1 = simple_fn_no_kwargs
    result = action.run(lib_entry_point="fake.module.fn1")
    assert result == "success_no_kwargs"


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


@patch("src.openstack_actions.OpenstackConnection")
@patch("src.openstack_actions.import_module")
def test_run_create_conn_when_valid(mock_import, mock_conn_cls, action):
    """when cloud_account and create_openstack_connection is passed conn is created and passed."""

    # pylint: disable=unused-argument
    def simple_openstack_fn(conn, a, b):
        return "success_openstack"

    mock_import.return_value.fn1 = simple_openstack_fn

    result = action.run(
        lib_entry_point="fake.module.fn1",
        cloud_account="dev",
        create_openstack_connection=True,
        a=1,
        b=2,
    )

    mock_conn_cls.assert_called_once_with("dev")
    # equality on the full call also proves cloud_account was removed
    assert result == "success_openstack"


@patch("src.openstack_actions.OpenstackConnection")
@patch("src.openstack_actions.import_module")
def test_run_doesnt_create_conn_when_valid(mock_import, mock_conn_cls, action):
    """when cloud_account is passed with no create_openstack_connection conn is NOT created"""

    # pylint: disable=unused-argument
    def simple_openstack_fn(cloud_account, a, b):
        return "success_openstack"

    mock_import.return_value.fn1 = simple_openstack_fn

    result = action.run(
        lib_entry_point="fake.module.fn1",
        cloud_account="dev",
        create_openstack_connection=False,
        a=1,
        b=2,
    )

    mock_conn_cls.assert_not_called()
    # equality on the full call also proves cloud_account was removed
    assert result == "success_openstack"


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
