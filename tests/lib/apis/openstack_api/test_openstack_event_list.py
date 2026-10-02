import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

import pytest
from openstack.exceptions import NotFoundException

from apis.openstack_api.enums.server_event import ServerEvent
from apis.openstack_api.openstack_event_list import EventList
from apis.openstack_api.structs.server_event_details import ServerEventDetails


class TestEventListBlackBox(unittest.TestCase):
    def setUp(self):
        # Setup a mock connection object shared across tests
        self.mock_conn = MagicMock()
        self.server_id = "test-server-123"

    def test_init_with_valid_server_id(self):
        """
        Scenario: The server ID exists in OpenStack.
        Expectation: Object initializes without raising exceptions.
        """
        # Configure mock API to simulate a valid server and an empty events generator
        self.mock_conn.compute.get_server.return_value = MagicMock()
        self.mock_conn.compute.server_actions.return_value = iter([])

        try:
            EventList(self.mock_conn, self.server_id)
        except NotFoundException as e:
            self.fail(f"Initialization raised an unexpected exception: {e}")

    def test_adding_list_with_bad_types(self):
        """
        Ensures the setter validates all the types in the list
        are of the expected type
        """
        with pytest.raises(AssertionError):
            EventList(MagicMock(), "").events = [None]

        with pytest.raises(AssertionError):
            EventList(MagicMock(), "").events = ["str"]

    def test_init_raises_exception_for_invalid_server_id(self):
        """
        Scenario: The server ID does not exist.
        Expectation: The OpenStack NotFoundException is propagated to the caller.
        """
        # Configure mock API to raise NotFoundException
        self.mock_conn.compute.get_server.side_effect = NotFoundException(
            "Server not found"
        )

        with self.assertRaises(NotFoundException):
            EventList(self.mock_conn, self.server_id)

    def test_last_event_returns_expected_value(self):
        """
        Tests that the events sort into the correct order
        """
        now = datetime.now()
        mock_event_1 = ServerEventDetails(MagicMock(), datetime.now())
        mock_event_2 = ServerEventDetails(MagicMock(), now + timedelta(days=1))
        mock_event_3 = ServerEventDetails(MagicMock(), now + timedelta(days=2))

        event_list = EventList(self.mock_conn, "")
        event_list.events = [mock_event_1, mock_event_3, mock_event_2]

        # We should get element 3 as it's the newest event (in the future)
        self.assertEqual(event_list.last_event, mock_event_3)


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

    events = EventList(conn, "server1").events

    expected_compute_find_call = conn.compute.get_server

    expected_compute_find_call.assert_called_once_with("server1")
    conn.compute.server_actions.assert_called_once_with(
        expected_compute_find_call.return_value
    )
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

    events = EventList(conn, "mock_sserver").events

    assert events[0].date == datetime(2026, 6, 1, 10, 0, 0, tzinfo=timezone.utc)


def test_get_server_event_list_ignores_unsupported_events():
    """
    Tests that unsupported events are marked as unknown
    """
    conn = MagicMock()
    conn.compute.server_actions.return_value = [
        MagicMock(action="os-reboot:reboot", start_time="2026-06-01T10:00:00.000000"),
        MagicMock(action="stop", start_time="2026-05-01T08:00:00.000000"),
    ]

    events = EventList(conn, "server1").events

    assert [event.event for event in events] == [ServerEvent.UNKNOWN, ServerEvent.STOP]


def test_get_server_event_list_returns_empty_list_when_no_actions():
    """
    Tests that we gracefully handle empty server event lists and return an empty list
    """
    conn = MagicMock()
    conn.compute.server_actions.return_value = []

    assert EventList(conn, "server1").events == []
