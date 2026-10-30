from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pytest
from openstack.exceptions import NotFoundException

from workflows.shutoff_all_non_wazuh_servers import (
    _shutoff_server,
    shutoff_all_non_wazuh_servers,
)

MODULE = "workflows.shutoff_all_non_wazuh_servers"

LOCK_REASON = "Server is not reporting to Wazuh - Please raise a ticket to get unlocked"


@pytest.fixture(name="mock_dependencies")
def fixture_mock_dependencies():
    """Mock all external dependencies."""
    with (
        patch(f"{MODULE}.get_all_servers") as get_all_servers,
        patch(f"{MODULE}.shutoff_server") as shutoff_server,
        patch(f"{MODULE}.admin_lock_server") as admin_lock_server,
        patch(f"{MODULE}.get_project_id") as get_project_id,
        patch(f"{MODULE}.wazuh_list_all_servers") as wazuh_list_all_servers,
        patch(f"{MODULE}.compare_2_lists") as compare_2_lists,
        patch(f"{MODULE}.read_config_file") as read_config_file,
        patch(f"{MODULE}.EventList") as event_list,
        patch(f"{MODULE}.logger") as logger,
    ):
        # Define the OpenStack and Wazuh server inventories.
        get_all_servers.side_effect = [
            ["server1", "server2", "server3", "amphora1"],
            ["amphora1"],
        ]
        wazuh_list_all_servers.return_value = ["server1"]
        get_project_id.return_value = "service-project-id"
        read_config_file.return_value = ["server3"]

        # Simulate the three filtering stages.
        compare_2_lists.side_effect = [
            (["server2", "server3", "amphora1"], [], []),
            (["server2", "server3"], [], []),
            (["server2"], [], []),
        ]

        # Default to an event older than five minutes.
        # This allows the server to be shut off.
        event_list.return_value.last_event.date = datetime.now(
            timezone.utc
        ) - timedelta(minutes=10)

        yield {
            "get_all_servers": get_all_servers,
            "wazuh_list_all_servers": wazuh_list_all_servers,
            "compare_2_lists": compare_2_lists,
            "get_project_id": get_project_id,
            "read_config_file": read_config_file,
            "shutoff_server": shutoff_server,
            "admin_lock_server": admin_lock_server,
            "event_list": event_list,
            "logger": logger,
        }


@pytest.mark.parametrize("admin_lock", [True, False])
def test_shutoff_all_non_wazuh_servers(mock_dependencies, admin_lock):
    """Verify eligible servers are shut off and optionally admin locked."""
    conn = MagicMock()
    wazuh_account = MagicMock()

    result = shutoff_all_non_wazuh_servers(conn, wazuh_account, admin_lock)

    # The function should return None.
    assert result is None

    # Verify OpenStack servers and Amphorae were retrieved.
    assert mock_dependencies["get_all_servers"].call_args_list == [
        call(conn, status="ACTIVE"),
        call(conn, "service-project-id"),
    ]

    # Verify the Wazuh inventory was retrieved.
    mock_dependencies["wazuh_list_all_servers"].assert_called_once_with(wazuh_account)

    # Verify the service project was identified.
    mock_dependencies["get_project_id"].assert_called_once_with(conn, "service")

    # Verify the configuration exclusion list was loaded.
    mock_dependencies["read_config_file"].assert_called_once_with(
        "SHUTOFF_ALL_NON_WAZUH_SERVER_EXCLUDE"
    )

    # Verify all three filtering stages.
    assert mock_dependencies["compare_2_lists"].call_args_list == [
        call(
            ["server1", "server2", "server3", "amphora1"],
            ["server1"],
        ),
        call(
            ["server2", "server3", "amphora1"],
            ["amphora1"],
        ),
        call(
            ["server2", "server3"],
            ["server3"],
        ),
    ]

    # Verify EventList was checked before shutting off the server.
    mock_dependencies["event_list"].assert_called_once_with(conn, "server2")

    # Only server2 should be shut off.
    mock_dependencies["shutoff_server"].assert_called_once_with(conn, "server2")

    # Admin locking should depend on the admin_lock flag.
    if admin_lock:
        mock_dependencies["admin_lock_server"].assert_called_once_with(
            conn, "server2", LOCK_REASON
        )
    else:
        mock_dependencies["admin_lock_server"].assert_not_called()

    # Verify the successfully shut off server was logged.
    mock_dependencies["logger"].info.assert_any_call(
        "list of servers that have been set SHUTOFF:\n\n%s",
        "server2",
    )

    mock_dependencies["logger"].error.assert_not_called()


def test_shutoff_all_non_wazuh_servers_empty_list(mock_dependencies):
    """Verify no actions occur when all servers are excluded."""
    conn = MagicMock()
    wazuh_account = MagicMock()

    # Simulate all servers being removed by the filters.
    mock_dependencies["compare_2_lists"].side_effect = [
        ([], [], []),
        ([], [], []),
        ([], [], []),
    ]

    result = shutoff_all_non_wazuh_servers(conn, wazuh_account, True)

    assert result is None

    # No event information should be retrieved.
    mock_dependencies["event_list"].assert_not_called()

    # No servers should be shut off or locked.
    mock_dependencies["shutoff_server"].assert_not_called()
    mock_dependencies["admin_lock_server"].assert_not_called()

    # Verify the empty list is logged.
    mock_dependencies["logger"].info.assert_any_call(
        "list of servers that have been set SHUTOFF:\n\n%s",
        "",
    )

    mock_dependencies["logger"].error.assert_not_called()


def test_shutoff_all_non_wazuh_servers_multiple_servers(mock_dependencies):
    """Verify every eligible server is shut off and locked."""
    conn = MagicMock()
    wazuh_account = MagicMock()

    # Simulate two eligible servers remaining after filtering.
    mock_dependencies["compare_2_lists"].side_effect = [
        (["server2", "server3", "amphora1"], [], []),
        (["server2", "server3"], [], []),
        (["server2", "server3"], [], []),
    ]

    result = shutoff_all_non_wazuh_servers(conn, wazuh_account, True)

    assert result is None

    # Verify event information was retrieved for both servers.
    assert mock_dependencies["event_list"].call_args_list == [
        call(conn, "server2"),
        call(conn, "server3"),
    ]

    # Verify both servers were shut off.
    assert mock_dependencies["shutoff_server"].call_args_list == [
        call(conn, "server2"),
        call(conn, "server3"),
    ]

    # Verify both servers were admin locked.
    assert mock_dependencies["admin_lock_server"].call_args_list == [
        call(conn, "server2", LOCK_REASON),
        call(conn, "server3", LOCK_REASON),
    ]

    # Verify both successful shutoffs were logged.
    mock_dependencies["logger"].info.assert_any_call(
        "list of servers that have been set SHUTOFF:\n\n%s",
        "server2\nserver3",
    )

    mock_dependencies["logger"].error.assert_not_called()


def test_shutoff_all_non_wazuh_servers_shutoff_failure(mock_dependencies):
    """
    Verify shutoff failures are logged and do not propagate.

    A failed shutoff must prevent admin locking of that server.
    """
    conn = MagicMock()
    wazuh_account = MagicMock()

    # Simulate an OpenStack API failure.
    mock_dependencies["shutoff_server"].side_effect = RuntimeError(
        "Failed to shut off server"
    )

    result = shutoff_all_non_wazuh_servers(conn, wazuh_account, True)

    assert result is None

    # Verify EventList was retrieved.
    mock_dependencies["event_list"].assert_called_once_with(conn, "server2")

    # Verify the shutoff was attempted.
    mock_dependencies["shutoff_server"].assert_called_once_with(conn, "server2")

    # A failed shutoff must not trigger admin locking.
    mock_dependencies["admin_lock_server"].assert_not_called()

    # Verify the failed server is excluded from the successful list.
    mock_dependencies["logger"].info.assert_any_call(
        "list of servers that have been set SHUTOFF:\n\n%s",
        "",
    )

    # Verify the failure was logged.
    mock_dependencies["logger"].error.assert_called_once_with(
        "unable to SHUTOFF server_id %s, skipping it",
        "server2",
    )


def test_shutoff_all_non_wazuh_servers_shutoff_failure_continues(
    mock_dependencies,
):
    """
    Verify a shutoff failure does not prevent processing subsequent servers.

    Only servers successfully shut off should be admin locked.
    """
    conn = MagicMock()
    wazuh_account = MagicMock()

    # Simulate three eligible servers.
    mock_dependencies["compare_2_lists"].side_effect = [
        (["server2", "server3", "server4"], [], []),
        (["server2", "server3", "server4"], [], []),
        (["server2", "server3", "server4"], [], []),
    ]

    # The first server fails, while the remaining servers succeed.
    mock_dependencies["shutoff_server"].side_effect = [
        RuntimeError("Failed to shut off server2"),
        None,
        None,
    ]

    result = shutoff_all_non_wazuh_servers(conn, wazuh_account, True)

    assert result is None

    # All three servers should have their event information checked.
    assert mock_dependencies["event_list"].call_args_list == [
        call(conn, "server2"),
        call(conn, "server3"),
        call(conn, "server4"),
    ]

    # All three servers should have a shutoff attempt.
    assert mock_dependencies["shutoff_server"].call_args_list == [
        call(conn, "server2"),
        call(conn, "server3"),
        call(conn, "server4"),
    ]

    # Only successfully shut off servers should be locked.
    assert mock_dependencies["admin_lock_server"].call_args_list == [
        call(conn, "server3", LOCK_REASON),
        call(conn, "server4", LOCK_REASON),
    ]

    # Only successful shutoffs should appear in the final list.
    mock_dependencies["logger"].info.assert_any_call(
        "list of servers that have been set SHUTOFF:\n\n%s",
        "server3\nserver4",
    )

    # Verify the failed server was logged.
    mock_dependencies["logger"].error.assert_called_once_with(
        "unable to SHUTOFF server_id %s, skipping it",
        "server2",
    )


def test_shutoff_all_non_wazuh_servers_admin_lock_failure(
    mock_dependencies,
):
    """
    Verify admin lock failures are logged and do not propagate.

    A successful shutoff followed by a failed lock should still
    be reported as a successful shutoff.
    """
    conn = MagicMock()
    wazuh_account = MagicMock()

    # Simulate an admin lock API failure.
    mock_dependencies["admin_lock_server"].side_effect = RuntimeError(
        "Failed to lock server"
    )

    result = shutoff_all_non_wazuh_servers(conn, wazuh_account, True)

    assert result is None

    # Shutoff should have succeeded before attempting the lock.
    mock_dependencies["shutoff_server"].assert_called_once_with(conn, "server2")

    # Verify admin locking was attempted.
    mock_dependencies["admin_lock_server"].assert_called_once_with(
        conn, "server2", LOCK_REASON
    )

    # A lock failure does not change the successful shutoff result.
    mock_dependencies["logger"].info.assert_any_call(
        "list of servers that have been set SHUTOFF:\n\n%s",
        "server2",
    )

    # Verify the lock failure was logged.
    mock_dependencies["logger"].error.assert_called_once_with(
        "unable to lock server_id %s, skipping it",
        "server2",
    )


def test_shutoff_all_non_wazuh_servers_admin_lock_failure_continues(
    mock_dependencies,
):
    """
    Verify an admin lock failure does not prevent subsequent servers
    from being shut off and locked.
    """
    conn = MagicMock()
    wazuh_account = MagicMock()

    # Simulate two eligible servers.
    mock_dependencies["compare_2_lists"].side_effect = [
        (["server2", "server3"], [], []),
        (["server2", "server3"], [], []),
        (["server2", "server3"], [], []),
    ]

    # The first lock fails, while the second succeeds.
    mock_dependencies["admin_lock_server"].side_effect = [
        RuntimeError("Failed to lock server2"),
        None,
    ]

    result = shutoff_all_non_wazuh_servers(conn, wazuh_account, True)

    assert result is None

    # Both servers should be shut off.
    assert mock_dependencies["shutoff_server"].call_args_list == [
        call(conn, "server2"),
        call(conn, "server3"),
    ]

    # Admin locking should be attempted for both servers.
    assert mock_dependencies["admin_lock_server"].call_args_list == [
        call(conn, "server2", LOCK_REASON),
        call(conn, "server3", LOCK_REASON),
    ]

    # Both servers were successfully shut off despite the lock failure.
    mock_dependencies["logger"].info.assert_any_call(
        "list of servers that have been set SHUTOFF:\n\n%s",
        "server2\nserver3",
    )

    # Only the first lock failure should be logged.
    mock_dependencies["logger"].error.assert_called_once_with(
        "unable to lock server_id %s, skipping it",
        "server2",
    )


def test_shutoff_all_non_wazuh_servers_shutoff_failure_without_admin_lock(
    mock_dependencies,
):
    """Verify shutoff failures are handled when admin locking is disabled."""
    conn = MagicMock()
    wazuh_account = MagicMock()

    mock_dependencies["shutoff_server"].side_effect = RuntimeError(
        "Failed to shut off server"
    )

    result = shutoff_all_non_wazuh_servers(conn, wazuh_account, False)

    assert result is None

    mock_dependencies["shutoff_server"].assert_called_once_with(conn, "server2")

    # Admin locking must never be attempted.
    mock_dependencies["admin_lock_server"].assert_not_called()

    # The shutoff failure should still be logged.
    mock_dependencies["logger"].error.assert_called_once_with(
        "unable to SHUTOFF server_id %s, skipping it",
        "server2",
    )

    # The failed server should not appear in the successful list.
    mock_dependencies["logger"].info.assert_any_call(
        "list of servers that have been set SHUTOFF:\n\n%s",
        "",
    )


# ---------------------------------------------------------------------------
# Tests for the new _shutoff_server helper.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("admin_lock", [True, False])
def test_shutoff_server_success(mock_dependencies, admin_lock):
    """
    Verify a server with an event older than five minutes is shut off.

    Admin locking should only occur when requested.
    """
    conn = MagicMock()

    result = _shutoff_server(conn, "server2", admin_lock)

    assert result is True

    mock_dependencies["event_list"].assert_called_once_with(conn, "server2")
    mock_dependencies["shutoff_server"].assert_called_once_with(conn, "server2")

    if admin_lock:
        mock_dependencies["admin_lock_server"].assert_called_once_with(
            conn, "server2", LOCK_REASON
        )
    else:
        mock_dependencies["admin_lock_server"].assert_not_called()

    mock_dependencies["logger"].error.assert_not_called()


@pytest.mark.parametrize("admin_lock", [True, False])
def test_shutoff_server_recent_event(mock_dependencies, admin_lock):
    """
    Verify servers with events less than five minutes old are skipped.

    Neither shutoff nor admin locking should be attempted.
    """
    conn = MagicMock()

    # Simulate an event that happened two minutes ago.
    mock_dependencies["event_list"].return_value.last_event.date = datetime.now(
        timezone.utc
    ) - timedelta(minutes=2)

    result = _shutoff_server(conn, "server2", admin_lock)

    assert result is False

    mock_dependencies["event_list"].assert_called_once_with(conn, "server2")
    mock_dependencies["shutoff_server"].assert_not_called()
    mock_dependencies["admin_lock_server"].assert_not_called()

    mock_dependencies["logger"].info.assert_any_call(
        "last event for server_id %s happened less than 5 minutes ago, skipping it",
        "server2",
    )

    mock_dependencies["logger"].error.assert_not_called()


@pytest.mark.parametrize("admin_lock", [True, False])
def test_shutoff_server_event_list_not_found(mock_dependencies, admin_lock):
    """
    Verify servers are skipped when EventList raises NotFoundException.

    No shutoff or admin locking should be attempted.
    """
    conn = MagicMock()

    # Simulate the event list being unavailable.
    mock_dependencies["event_list"].side_effect = NotFoundException(
        "Event list not found"
    )

    result = _shutoff_server(conn, "server2", admin_lock)

    assert result is False

    mock_dependencies["event_list"].assert_called_once_with(conn, "server2")
    mock_dependencies["shutoff_server"].assert_not_called()
    mock_dependencies["admin_lock_server"].assert_not_called()

    mock_dependencies["logger"].error.assert_called_once_with(
        "unable to find Event List information for server_id %s, skipping it",
        "server2",
    )


@pytest.mark.parametrize("admin_lock", [True, False])
def test_shutoff_server_failure(mock_dependencies, admin_lock):
    """
    Verify shutoff failures return False.

    Admin locking must not be attempted when shutoff fails.
    """
    conn = MagicMock()

    mock_dependencies["shutoff_server"].side_effect = RuntimeError(
        "Failed to shut off server"
    )

    result = _shutoff_server(conn, "server2", admin_lock)

    assert result is False

    mock_dependencies["event_list"].assert_called_once_with(conn, "server2")
    mock_dependencies["shutoff_server"].assert_called_once_with(conn, "server2")
    mock_dependencies["admin_lock_server"].assert_not_called()

    mock_dependencies["logger"].error.assert_called_once_with(
        "unable to SHUTOFF server_id %s, skipping it",
        "server2",
    )


def test_shutoff_server_admin_lock_failure(mock_dependencies):
    """
    Verify a failed admin lock does not change the shutoff result.

    The helper should return True because the server was shut off.
    """
    conn = MagicMock()

    mock_dependencies["admin_lock_server"].side_effect = RuntimeError(
        "Failed to lock server"
    )

    result = _shutoff_server(conn, "server2", True)

    assert result is True

    mock_dependencies["shutoff_server"].assert_called_once_with(conn, "server2")
    mock_dependencies["admin_lock_server"].assert_called_once_with(
        conn, "server2", LOCK_REASON
    )

    mock_dependencies["logger"].error.assert_called_once_with(
        "unable to lock server_id %s, skipping it",
        "server2",
    )


def test_shutoff_all_non_wazuh_servers_recent_event(mock_dependencies):
    """
    Verify servers with recent events are excluded from the final list.

    Other eligible servers should continue to be processed.
    """
    conn = MagicMock()
    wazuh_account = MagicMock()

    # Simulate two eligible servers.
    mock_dependencies["compare_2_lists"].side_effect = [
        (["server2", "server3"], [], []),
        (["server2", "server3"], [], []),
        (["server2", "server3"], [], []),
    ]

    # Server2 has a recent event, while server3 has an older event.
    recent_event = SimpleNamespace(
        last_event=SimpleNamespace(
            date=datetime.now(timezone.utc) - timedelta(minutes=2)
        )
    )
    old_event = SimpleNamespace(
        last_event=SimpleNamespace(
            date=datetime.now(timezone.utc) - timedelta(minutes=10)
        )
    )

    mock_dependencies["event_list"].side_effect = [
        recent_event,
        old_event,
    ]

    result = shutoff_all_non_wazuh_servers(conn, wazuh_account, True)

    assert result is None

    # Both servers should have their event lists checked.
    assert mock_dependencies["event_list"].call_args_list == [
        call(conn, "server2"),
        call(conn, "server3"),
    ]

    # Only server3 should be shut off and locked.
    mock_dependencies["shutoff_server"].assert_called_once_with(conn, "server3")
    mock_dependencies["admin_lock_server"].assert_called_once_with(
        conn, "server3", LOCK_REASON
    )

    # Only server3 should appear in the successful list.
    mock_dependencies["logger"].info.assert_any_call(
        "list of servers that have been set SHUTOFF:\n\n%s",
        "server3",
    )

    mock_dependencies["logger"].error.assert_not_called()


def test_shutoff_all_non_wazuh_servers_event_list_not_found_continues(
    mock_dependencies,
):
    """
    Verify a missing EventList does not stop processing other servers.

    Only servers with available, sufficiently old events are shut off.
    """
    conn = MagicMock()
    wazuh_account = MagicMock()

    mock_dependencies["compare_2_lists"].side_effect = [
        (["server2", "server3"], [], []),
        (["server2", "server3"], [], []),
        (["server2", "server3"], [], []),
    ]

    # The first server has no EventList, while the second is eligible.
    old_event = SimpleNamespace(
        last_event=SimpleNamespace(
            date=datetime.now(timezone.utc) - timedelta(minutes=10)
        )
    )

    mock_dependencies["event_list"].side_effect = [
        NotFoundException("Event list not found"),
        old_event,
    ]

    result = shutoff_all_non_wazuh_servers(conn, wazuh_account, True)

    assert result is None

    # Both servers should be checked.
    assert mock_dependencies["event_list"].call_args_list == [
        call(conn, "server2"),
        call(conn, "server3"),
    ]

    # Only server3 should be shut off and locked.
    mock_dependencies["shutoff_server"].assert_called_once_with(conn, "server3")
    mock_dependencies["admin_lock_server"].assert_called_once_with(
        conn, "server3", LOCK_REASON
    )

    # Verify only the successful shutoff is reported.
    mock_dependencies["logger"].info.assert_any_call(
        "list of servers that have been set SHUTOFF:\n\n%s",
        "server3",
    )

    # Verify the missing event list was logged.
    mock_dependencies["logger"].error.assert_called_once_with(
        "unable to find Event List information for server_id %s, skipping it",
        "server2",
    )
