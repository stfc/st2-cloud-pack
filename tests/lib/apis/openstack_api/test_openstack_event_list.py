import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from openstack.exceptions import NotFoundException

from apis.openstack_api.openstack_event_list import EventList


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
        Scenario: API returns a list of events.
        Expectation: last_event property returns the first item from the API's feed.
        """
        # Mocking the ServerAction objects returned by the API
        mock_event_1 = MagicMock()
        mock_event_2 = MagicMock()

        self.mock_conn.compute.get_server.return_value = MagicMock()
        self.mock_conn.compute.server_actions.return_value = iter(
            [mock_event_1, mock_event_2]
        )

        event_list = EventList(self.mock_conn, self.server_id)

        # Act & Assert
        self.assertEqual(event_list.last_event, mock_event_1)

    @patch("apis.openstack_api.openstack_event_list.datetime")
    def test_seconds_in_current_state_calculation(self, mock_datetime):
        """
        Scenario: The last event occurred at a specific ISO timestamp.
        Expectation: seconds_in_current_state accurately calculates the delta against 'now'.
        """
        # 1. Mock the 'current' time to a fixed point (2026-06-15 12:00:00 UTC)
        fixed_now = datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_now
        # We also need to preserve the real fromisoformat behavior for the test to work
        mock_datetime.fromisoformat = datetime.fromisoformat

        # 2. Mock the event from OpenStack to have happened exactly 45 minutes (2700 seconds) prior
        # 2026-06-15T11:15:00.000000
        mock_event = MagicMock()
        mock_event.start_time = "2026-06-15T11:15:00.000000"

        self.mock_conn.compute.get_server.return_value = MagicMock()
        self.mock_conn.compute.server_actions.return_value = iter([mock_event])

        # 3. Initialize and assert public outputs
        event_list = EventList(self.mock_conn, self.server_id)
        expected_seconds = 45 * 60  # 2700 seconds

        self.assertEqual(event_list.seconds_in_current_state, expected_seconds)
