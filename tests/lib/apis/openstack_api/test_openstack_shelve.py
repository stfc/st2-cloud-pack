from datetime import datetime, timezone
from unittest.mock import MagicMock, NonCallableMock, patch

import pytest
from apis.openstack_api.enums.server_event import ServerEvent
from apis.openstack_api.structs.server_event_details import ServerEventDetails
from apis.openstack_api.openstack_server import (
    shelve_server,
    get_server_event_list,
    get_server_metadata,
)
from openstack.exceptions import (
    ResourceFailure,
    ResourceNotFound,
    ResourceTimeout,
)


def _mock_connection(status: str) -> MagicMock:
    conn = MagicMock()
    mock_server = MagicMock()
    mock_server.id = "server1"
    mock_server.name = "vm1"
    mock_server.status = status
    conn.compute.find_server.return_value = mock_server
    return conn


def _mock_server(server_id: str = "server1") -> MagicMock:
    server = MagicMock()
    server.id = server_id
    return server


def test_shelve_server_raises_when_server_does_not_exist():
    """
    Tests that a missing server raises ResourceNotFound
    instead of AttributeError if a server isn't found
    """
    conn = _mock_connection("SHUTOFF")
    conn.compute.find_server.side_effect = ResourceNotFound("no such server")
    all_projects = NonCallableMock()

    with pytest.raises(ResourceNotFound):
        shelve_server(conn, "server1", all_projects=all_projects)

    conn.compute.find_server.assert_called_once_with(
        "server1", ignore_missing=False, all_projects=all_projects
    )
    conn.compute.shelve_server.assert_not_called()


def test_shelve_server_shelves_shutoff_server():
    """
    Tests that a SHUTOFF server is shelved and we wait for
    a SHELVED or SHELVED_OFFLOADED state before returning
    """
    conn = _mock_connection("SHUTOFF")
    conn.compute.get_server.return_value.status = "SHELVED"
    all_projects = NonCallableMock()

    with patch("apis.openstack_api.openstack_server.time.sleep"):
        assert shelve_server(conn, "server1", all_projects=all_projects) is None

    conn.compute.find_server.assert_called_once_with(
        "server1", ignore_missing=False, all_projects=all_projects
    )
    conn.compute.shelve_server.assert_called_once_with(
        conn.compute.find_server.return_value
    )
    conn.compute.get_server.assert_called_with("server1")
    conn.compute.set_server_metadata.assert_not_called()


def test_shelve_server_waits_for_shelved_offloaded():
    """
    Tests that SHELVED_OFFLOADED is treated as a valid shelved state
    """
    conn = _mock_connection("SHUTOFF")
    conn.compute.get_server.return_value.status = "SHELVED_OFFLOADED"

    with patch("apis.openstack_api.openstack_server.time.sleep"):
        shelve_server(conn, "server1")

    conn.compute.shelve_server.assert_called_once()
    conn.compute.set_server_metadata.assert_not_called()


def test_shelve_server_skips_shelving_already_sheled_server():
    """
    Tests that a SHELVED server is skipped
    """
    conn = _mock_connection("SHELVED")

    shelve_server(conn, "server1")

    conn.compute.shelve_server.assert_not_called()
    conn.compute.get_server.assert_not_called()
    conn.compute.set_server_metadata.assert_not_called()


def test_shelve_server_skips_shelving_already_offloaded_server():
    """
    Tests a SHELVED_OFFLOADED server is skipped
    """
    conn = _mock_connection("SHELVED_OFFLOADED")

    shelve_server(conn, "server1")

    conn.compute.shelve_server.assert_not_called()
    conn.compute.get_server.assert_not_called()
    conn.compute.set_server_metadata.assert_not_called()


def test_shelve_server_raises_when_server_not_shutoff():
    """
    Tests that a server which is not SHUTOFF or already shelved raises ValueError
    """
    conn = _mock_connection("ACTIVE")

    with pytest.raises(ValueError, match="must be SHUTOFF"):
        shelve_server(conn, "server1")

    conn.compute.shelve_server.assert_not_called()
    conn.compute.set_server_metadata.assert_not_called()


def test_shelve_server_raises_when_server_reaches_error():
    """
    Tests that a server reaching ERROR state while shelving raises
    ResourceFailure rather than waiting until the action timeout
    """
    conn = _mock_connection("SHUTOFF")
    conn.compute.get_server.return_value.status = "ERROR"

    with patch("apis.openstack_api.openstack_server.time.sleep"), pytest.raises(
        ResourceFailure
    ):
        shelve_server(conn, "server1")

    conn.compute.shelve_server.assert_called_once()


def test_shelve_server_times_out_waiting_for_shelved_state():
    """
    Tests that a server which never reaches a shelved state raises
    ResourceTimeout
    """
    conn = _mock_connection("SHUTOFF")
    conn.compute.get_server.return_value.status = "SHUTOFF"
    clock = {"t": 0.0}

    with patch(
        "apis.openstack_api.openstack_server.time.sleep",
        # Each time we call sleep we'll increment the clock by the sleep time
        side_effect=lambda s: clock.__setitem__("t", clock["t"] + s),
    ), patch(
        "apis.openstack_api.openstack_server.time.time",
        side_effect=lambda: clock["t"],
    ), pytest.raises(
        ResourceTimeout
    ):
        shelve_server(conn, "server1")

    conn.compute.shelve_server.assert_called_once()


def test_get_server_event_list_returns_all_supported_events():
    """
    Tests the get_server_event_list function returns all supported events
    with the datetime from the OpenStack API in a sorted order
    """
    conn = MagicMock()
    conn.compute.server_actions.return_value = [
        MagicMock(action="stop", start_time="2026-06-01T10:00:00.000000"),
        MagicMock(action="start", start_time="2026-05-20T09:30:00.000000"),
        MagicMock(action="shelve", start_time="2026-05-10T07:00:00.000000"),
        MagicMock(action="unshelve", start_time="2026-05-08T06:00:00.000000"),
        MagicMock(action="shelveOffload", start_time="2026-05-01T08:00:00.000000"),
    ]

    events = get_server_event_list(conn, _mock_server())

    conn.compute.server_actions.assert_called_once_with("server1")
    assert all(isinstance(event, ServerEventDetails) for event in events)
    assert [event.event for event in events] == [
        ServerEvent.STOP,
        ServerEvent.START,
        ServerEvent.SHELVE,
        ServerEvent.UNSHELVE,
        ServerEvent.SHELVE_OFFLOAD,
    ]
    assert events[0].date == datetime(2026, 6, 1, 10, 0, 0, tzinfo=timezone.utc)


def test_get_server_event_list_parses_z_suffix_timestamps():
    """
    Tests that timestamps with a 'Z' suffix are parsed as UTC
    """
    conn = MagicMock()
    conn.compute.server_actions.return_value = [
        MagicMock(action="stop", start_time="2026-06-01T10:00:00Z"),
    ]

    events = get_server_event_list(conn, _mock_server())

    assert events[0].date == datetime(2026, 6, 1, 10, 0, 0, tzinfo=timezone.utc)


def test_get_server_event_list_ignores_unsupported_events():
    """
    Tests that unsupported events are ignored when fetching server events
    """
    conn = MagicMock()
    conn.compute.server_actions.return_value = [
        MagicMock(action="os-reboot:reboot", start_time="2026-06-01T10:00:00.000000"),
        MagicMock(action="stop", start_time="2026-05-01T08:00:00.000000"),
    ]

    events = get_server_event_list(conn, _mock_server())

    assert [event.event for event in events] == [ServerEvent.STOP]


def test_get_server_event_list_returns_empty_list_when_no_actions():
    """
    Tests that we gracefully handle empty server event lists and return an empty list
    """
    conn = MagicMock()
    conn.compute.server_actions.return_value = []

    assert get_server_event_list(conn, _mock_server()) == []


def test_get_server_metadata():
    """
    Tests the get_server_metadata returns the metadata of a server as a dictionary of key:values
    """
    conn = MagicMock()
    conn.compute.find_server.return_value.metadata = {"key": "value"}
    all_projects = NonCallableMock()

    metadata = get_server_metadata(conn, "server1", all_projects=all_projects)

    conn.compute.find_server.assert_called_once_with(
        "server1", ignore_missing=False, all_projects=all_projects
    )
    assert metadata == {"key": "value"}


def test_get_server_metadata_returns_empty_dict_when_metadata_is_none():
    """
    Tests that get_server_metadata returns an empty dictionary when the server metadata is None
    """
    conn = MagicMock()
    conn.compute.find_server.return_value.metadata = None

    assert get_server_metadata(conn, "server1") == {}
