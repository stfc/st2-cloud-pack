import unittest
from typing import Callable
from unittest.mock import patch, NonCallableMock, Mock

from openstack_query.handlers.client_side_handler_datetime import (
    ClientSideHandlerDateTime,
)
from enums.query.query_presets import QueryPresetsDateTime

from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access, unused-argument


@patch("openstack_query.time_utils.TimeUtils.get_timestamp_in_seconds")
@patch("openstack_query.handlers.client_side_handler_datetime.datetime")
class ClientSideHandlerDateTimeTests(unittest.TestCase):
    """
    Run various tests to ensure that ClientSideHandlerDateTime class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        # sets filter function mappings so that PROP_1 is valid for all client_side
        _filter_function_mappings = {
            preset: [MockProperties.PROP_1] for preset in QueryPresetsDateTime
        }
        self.instance = ClientSideHandlerDateTime(_filter_function_mappings)

    def test_check_supported_all_presets(self, *_):
        """
        Tests that client_side_handler_datetime supports all datetime QueryPresets
        """
        self.assertTrue(
            self.instance.check_supported(preset, MockProperties.PROP_1)
            for preset in QueryPresetsDateTime
        )

    @staticmethod
    def _run_prop_case_with_mocks(
        method: Callable,
        mock_datetime: Mock,
        mock_time_get_timestamp: Mock,
        prop_time: int,
        user_time: int,
    ):
        """
        Runs the test case with mocks to ensure the prop time handling works as expected
        Does not assert the final result, that is for the test case to do
        """
        prop_str = NonCallableMock()
        days, hours, mins, secs = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        mock_datetime.strptime.return_value.timestamp.return_value = (
            prop_time  # Prop timestamp
        )
        mock_time_get_timestamp.return_value = (
            user_time  # The user's selected timeframe
        )

        result = method(prop_str, days, hours, mins, secs)

        assert mock_datetime.strptime.timestamp.called_once_with(
            prop_str, "%Y-%m-%dT%H:%M:%SZ"
        )
        assert mock_datetime.strptime.return_value.timestamp.called_once_with()
        assert mock_time_get_timestamp.called_once_with(days, hours, mins, secs)

        return result

    def test_prop_older_than_with_actual_older(self, mock_datetime, mock_get_timestamp):
        """
        Tests that function prop_older_than functions expectedly
        Returns True if prop is older than a calculated relative time from current time (set to 2023-06-04 10:30AM)
        """
        assert self._run_prop_case_with_mocks(
            self.instance._prop_older_than, mock_datetime, mock_get_timestamp, 300, 200
        )

    def test_prop_older_than_with_actual_younger(
        self, mock_datetime, mock_get_timestamp
    ):
        """
        Tests that function prop_older_than functions expectedly
        Returns True if prop is older than a calculated relative time from current time (set to 2023-06-04 10:30AM)
        """
        assert not self._run_prop_case_with_mocks(
            self.instance._prop_older_than, mock_datetime, mock_get_timestamp, 100, 200
        )

    def test_prop_younger_than(self, mock_datetime, mock_get_timestamp):
        """
        Tests that function prop_older_than functions expectedly
        Returns True if prop is older than a calculated relative time from current time (set to 2023-06-04 10:30AM)
        """
        assert self._run_prop_case_with_mocks(
            self.instance._prop_younger_than,
            mock_datetime,
            mock_get_timestamp,
            100,
            200,
        )

    def test_prop_younger_than_with_actual_older(
        self, mock_datetime, mock_get_timestamp
    ):
        """
        Tests that function prop_older_than functions expectedly
        Returns True if prop is older than a calculated relative time from current time (set to 2023-06-04 10:30AM)
        """
        assert not self._run_prop_case_with_mocks(
            self.instance._prop_younger_than,
            mock_datetime,
            mock_get_timestamp,
            300,
            200,
        )

    def test_prop_younger_than_or_equal_to(self, *_):
        """
        Tests that function prop_younger_than_or_equal_to functions expectedly by inverting older than
        """
        prop, days, hours, mins, secs = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        with patch.object(self.instance, "_prop_older_than") as mock_prop_older_than:
            mock_prop_older_than.return_value = False

            assert self.instance._prop_younger_than_or_equal_to(
                prop, days, hours, mins, secs
            )
            mock_prop_older_than.assert_called_once_with(prop, days, hours, mins, secs)

    def test_prop_older_than_or_equal_to(self, *_):
        prop, days, hours, mins, secs = (
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
            NonCallableMock(),
        )
        with patch.object(
            self.instance, "_prop_younger_than"
        ) as mock_prop_younger_than:
            mock_prop_younger_than.return_value = False

            assert self.instance._prop_older_than_or_equal_to(
                prop, days, hours, mins, secs
            )
            mock_prop_younger_than.assert_called_once_with(
                prop, days, hours, mins, secs
            )
