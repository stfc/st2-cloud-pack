import unittest
from datetime import datetime
from unittest.mock import patch
from parameterized import parameterized

from openstack_query.handlers.client_side_handler_datetime import (
    ClientSideHandlerDateTime,
)

from tests.lib.openstack_query.mocks.mocked_props import MockProperties

from enums.query.query_presets import QueryPresetsDateTime


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
        _FILTER_FUNCTION_MAPPINGS = {
            preset: [MockProperties.PROP_1] for preset in QueryPresetsDateTime
        }
        self.instance = ClientSideHandlerDateTime(_FILTER_FUNCTION_MAPPINGS)

    @parameterized.expand(
        [(f"test {preset.name}", preset) for preset in QueryPresetsDateTime]
    )
    def test_check_supported_all_presets(self, name, preset):
        """
        Tests that handler supports all generic query client_side
        """
        self.assertTrue(self.instance.check_supported(preset, MockProperties.PROP_1))

    @parameterized.expand(
        [
            (
                "prop timestamp is older by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-04T10:30:00Z",
                True,
            ),
            (
                "prop timestamp is older by 12 hours",
                0,
                12,
                0,
                0,
                "2023-06-04T10:30:00Z",
                True,
            ),
            (
                "prop timestamp is younger by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-02T10:30:00Z",
                False,
            ),
            (
                "prop timestamp is equal",
                0,
                0,
                30,
                0,
                "2023-06-04T10:00:00Z",
                False,
            ),
            (
                "prop timestamp is older by 0.5 seconds",
                0,
                0,
                0,
                0.5,
                "2023-06-04T10:30:00Z",
                True,
            ),
        ]
    )
    @patch("openstack_query.time_utils.TimeUtils.get_current_time")
    def test_prop_older_than(
        self,
        name,
        days,
        hours,
        minutes,
        seconds,
        string_timestamp,
        expected_out,
        mock_current_datetime,
    ):
        # sets a consistent specific datetime
        mock_current_datetime.return_value = datetime(2023, 6, 4, 10, 30, 0)

        out = self.instance._prop_older_than(
            prop=string_timestamp,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )
        assert out == expected_out

    @parameterized.expand(
        [
            (
                "prop timestamp is older by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-04T10:30:00Z",
                True,
            ),
            (
                "prop timestamp is older by 12 hours",
                0,
                12,
                0,
                0,
                "2023-06-04T10:30:00Z",
                True,
            ),
            (
                "prop timestamp is younger by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-02T10:30:00Z",
                False,
            ),
            (
                "prop timestamp is equal",
                0,
                0,
                30,
                0,
                "2023-06-04T10:00:00Z",
                True,
            ),
            (
                "prop timestamp is older by 0.5 seconds",
                0,
                0,
                0,
                0.5,
                "2023-06-04T10:30:00Z",
                True,
            ),
        ]
    )
    @patch("openstack_query.time_utils.TimeUtils.get_current_time")
    def test_prop_older_than_or_equal_to(
        self,
        name,
        days,
        hours,
        minutes,
        seconds,
        string_timestamp,
        expected_out,
        mock_current_datetime,
    ):
        # sets a consistent specific datetime
        mock_current_datetime.return_value = datetime(2023, 6, 4, 10, 30, 0)

        out = self.instance._prop_older_than_or_equal_to(
            prop=string_timestamp,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )
        assert out == expected_out

    @parameterized.expand(
        [
            (
                "prop timestamp is younger by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-02T10:30:00Z",
                True,
            ),
            (
                "prop timestamp is younger by 12 hours",
                0,
                12,
                0,
                0,
                "2023-06-03T10:30:00Z",
                True,
            ),
            (
                "prop timestamp is older by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-04T10:30:00Z",
                False,
            ),
            (
                "prop timestamp is equal",
                0,
                0,
                30,
                0,
                "2023-06-04T10:00:00Z",
                False,
            ),
            (
                "prop timestamp is younger by .5 seconds",
                0,
                0,
                0,
                0.5,
                "2023-06-03T10:29:59Z",
                True,
            ),
        ]
    )
    @patch("openstack_query.time_utils.TimeUtils.get_current_time")
    def test_prop_younger_than(
        self,
        name,
        days,
        hours,
        minutes,
        seconds,
        string_timestamp,
        expected_out,
        mock_current_time,
    ):
        # sets a consistent specific datetime
        mock_current_time.return_value = datetime(2023, 6, 4, 10, 30, 0)

        out = self.instance._prop_younger_than(
            prop=string_timestamp,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )
        assert out == expected_out

    @parameterized.expand(
        [
            (
                "prop timestamp is younger by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-02T10:30:00Z",
                True,
            ),
            (
                "prop timestamp is younger by 12 hours",
                0,
                12,
                0,
                0,
                "2023-06-03T10:30:00Z",
                True,
            ),
            (
                "prop timestamp is older by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-04T10:30:00Z",
                False,
            ),
            (
                "prop timestamp is equal",
                0,
                0,
                30,
                0,
                "2023-06-04T10:00:00Z",
                True,
            ),
            (
                "prop timestamp is younger by .5 seconds",
                0,
                0,
                0,
                0.5,
                "2023-06-03T10:29:59Z",
                True,
            ),
        ]
    )
    @patch("openstack_query.time_utils.TimeUtils.get_current_time")
    def test_prop_younger_than_or_equal_to(
        self,
        name,
        days,
        hours,
        minutes,
        seconds,
        string_timestamp,
        expected_out,
        mock_current_time,
    ):
        # sets a consistent specific datetime
        mock_current_time.return_value = datetime(2023, 6, 4, 10, 30, 0)

        out = self.instance._prop_younger_than_or_equal_to(
            prop=string_timestamp,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )
        assert out == expected_out
