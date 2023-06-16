import unittest
from datetime import datetime
from unittest.mock import patch
from parameterized import parameterized

from nose.tools import raises

from openstack_query.handlers.presets.preset_handler_datetime import (
    PresetHandlerDateTime,
)
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

from enums.query.query_presets import QueryPresetsDateTime
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError


class PresetHandlerGenericTests(unittest.TestCase):
    """
    Run various tests to ensure that PresetHandlerGeneric class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        # sets filter function mappings so that PROP_1 is valid for all presets
        _FILTER_FUNCTION_MAPPINGS = {
            preset: [MockProperties.PROP_1] for preset in QueryPresetsDateTime
        }
        self.instance = PresetHandlerDateTime(_FILTER_FUNCTION_MAPPINGS)

    @parameterized.expand(
        [(f"test {preset.name}", preset) for preset in QueryPresetsDateTime]
    )
    def test_check_supported_all_presets(self, name, preset):
        """
        Tests that handler supports all generic query presets
        """
        self.assertTrue(self.instance.check_supported(preset, MockProperties.PROP_1))

    @parameterized.expand(
        [(f"test {preset.name}", preset) for preset in QueryPresetsDateTime]
    )
    def test_get_mapping_all_presets(self, name, preset):
        """
        Tests that handler supports all generic query presets
        """
        self.assertIsNotNone(self.instance._get_mapping(preset, MockProperties.PROP_1))

    @parameterized.expand(
        [
            ("1 day = 86400 seconds", 1, 0, 0, 0, 86400),
            ("12 hours = 43200 seconds", 0, 12, 0, 0, 43200),
            ("2 days, 30 minutes = 174600 seconds", 2, 0, 30, 0, 174600),
            ("20 seconds", 0, 0, 0, 20, 20),
        ]
    )
    @patch(
        "openstack_query.handlers.presets.preset_handler_datetime.PresetHandlerDateTime._get_current_time"
    )
    def test_get_timestamp_in_seconds(
        self, name, days, hours, minutes, seconds, total_seconds, mock_current_datetime
    ):
        mock_current_datetime.return_value = datetime(2023, 6, 4, 10, 30, 0)
        out = self.instance._get_timestamp_in_seconds(days, hours, minutes, seconds)

        mock_current_datetime.assert_called_once()

        expected_timestamp = (
            mock_current_datetime.return_value.timestamp() - total_seconds
        )
        assert out == expected_timestamp

    @raises(MissingMandatoryParamError)
    def test_get_timestamp_in_seconds_invalid(self):
        self.instance._get_timestamp_in_seconds(days=0, hours=0, minutes=0, seconds=0)

    @parameterized.expand(
        [
            (
                "prop timestamp is older by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-04 10:30:00",
                "%Y-%m-%d %H:%M:%S",
                True,
            ),
            (
                "prop timestamp is older by 12 hours",
                0,
                12,
                0,
                0,
                "2023-06-04 10:30:00 AM",
                "%Y-%m-%d %I:%M:%S %p",
                True,
            ),
            (
                "prop timestamp is younger by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-02",
                "%Y-%m-%d",
                False,
            ),
            (
                "prop timestamp is equal",
                0,
                0,
                30,
                0,
                "2023-06-04 10:00:00",
                "%Y-%m-%d %H:%M:%S",
                False,
            ),
            (
                "prop timestamp is older by 0.5 seconds",
                0,
                0,
                0,
                0.5,
                "2023-06-04 10:30:00",
                "%Y-%m-%d %H:%M:%S",
                True,
            ),
        ]
    )
    @patch(
        "openstack_query.handlers.presets.preset_handler_datetime.PresetHandlerDateTime._get_current_time"
    )
    def test_prop_older_than(
        self,
        name,
        days,
        hours,
        minutes,
        seconds,
        string_timestamp,
        timestamp_format,
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
            prop_timestamp_fmt=timestamp_format,
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
                "2023-06-04 10:30:00",
                "%Y-%m-%d %H:%M:%S",
                True,
            ),
            (
                "prop timestamp is older by 12 hours",
                0,
                12,
                0,
                0,
                "2023-06-04 10:30:00 AM",
                "%Y-%m-%d %I:%M:%S %p",
                True,
            ),
            (
                "prop timestamp is younger by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-02",
                "%Y-%m-%d",
                False,
            ),
            (
                "prop timestamp is equal",
                0,
                0,
                30,
                0,
                "2023-06-04 10:00:00",
                "%Y-%m-%d %H:%M:%S",
                True,
            ),
            (
                "prop timestamp is older by 0.5 seconds",
                0,
                0,
                0,
                0.5,
                "2023-06-04 10:30:00",
                "%Y-%m-%d %H:%M:%S",
                True,
            ),
        ]
    )
    @patch(
        "openstack_query.handlers.presets.preset_handler_datetime.PresetHandlerDateTime._get_current_time"
    )
    def test_prop_older_than_or_equal_to(
        self,
        name,
        days,
        hours,
        minutes,
        seconds,
        string_timestamp,
        timestamp_format,
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
            prop_timestamp_fmt=timestamp_format,
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
                "2023-06-02 10:30:00",
                "%Y-%m-%d %H:%M:%S",
                True,
            ),
            (
                "prop timestamp is younger by 12 hours",
                0,
                12,
                0,
                0,
                "2023-06-03 10:30:00 AM",
                "%Y-%m-%d %I:%M:%S %p",
                True,
            ),
            (
                "prop timestamp is older by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-04",
                "%Y-%m-%d",
                False,
            ),
            (
                "prop timestamp is equal",
                0,
                0,
                30,
                0,
                "2023-06-04 10:00:00",
                "%Y-%m-%d %H:%M:%S",
                False,
            ),
            (
                "prop timestamp is younger by .5 seconds",
                0,
                0,
                0,
                0.5,
                "2023-06-03 10:29:59",
                "%Y-%m-%d %H:%M:%S",
                True,
            ),
        ]
    )
    @patch(
        "openstack_query.handlers.presets.preset_handler_datetime.PresetHandlerDateTime._get_current_time"
    )
    def test_prop_younger_than(
        self,
        name,
        days,
        hours,
        minutes,
        seconds,
        string_timestamp,
        timestamp_format,
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
            prop_timestamp_fmt=timestamp_format,
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
                "2023-06-02 10:30:00",
                "%Y-%m-%d %H:%M:%S",
                True,
            ),
            (
                "prop timestamp is younger by 12 hours",
                0,
                12,
                0,
                0,
                "2023-06-03 10:30:00 AM",
                "%Y-%m-%d %I:%M:%S %p",
                True,
            ),
            (
                "prop timestamp is older by 1 day",
                1,
                0,
                0,
                0,
                "2023-06-04",
                "%Y-%m-%d",
                False,
            ),
            (
                "prop timestamp is equal",
                0,
                0,
                30,
                0,
                "2023-06-04 10:00:00",
                "%Y-%m-%d %H:%M:%S",
                True,
            ),
            (
                "prop timestamp is younger by .5 seconds",
                0,
                0,
                0,
                0.5,
                "2023-06-03 10:29:59",
                "%Y-%m-%d %H:%M:%S",
                True,
            ),
        ]
    )
    @patch(
        "openstack_query.handlers.presets.preset_handler_datetime.PresetHandlerDateTime._get_current_time"
    )
    def test_prop_younger_than_or_equal_to(
        self,
        name,
        days,
        hours,
        minutes,
        seconds,
        string_timestamp,
        timestamp_format,
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
            prop_timestamp_fmt=timestamp_format,
        )
        assert out == expected_out
