import unittest
from datetime import datetime

from unittest.mock import patch
from parameterized import parameterized
from nose.tools import raises

from openstack_query.time_utils import TimeUtils
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError


class TimeUtilsTests(unittest.TestCase):
    """
    Runs various tests to ensure that utils module functions expectedly
    """

    @parameterized.expand(
        [
            ("1 day = 86400 seconds", 1, 0, 0, 0, 86400),
            ("12 hours = 43200 seconds", 0, 12, 0, 0, 43200),
            ("2 days, 30 minutes = 174600 seconds", 2, 0, 30, 0, 174600),
            ("20 seconds", 0, 0, 0, 20, 20),
        ]
    )
    @patch("openstack_query.time_utils.TimeUtils.get_current_time")
    def test_get_timestamp_in_seconds(
        self, name, days, hours, minutes, seconds, total_seconds, mock_current_datetime
    ):
        """
        Tests that get_timestamp_in_seconds method works expectedly
        method takes a set of integer params "days, hours, minutes, seconds" and calculates total seconds
        """
        mock_current_datetime.return_value = datetime(2023, 6, 4, 10, 30, 0)
        out = TimeUtils.get_timestamp_in_seconds(days, hours, minutes, seconds)

        mock_current_datetime.assert_called_once()

        expected_timestamp = (
            mock_current_datetime.return_value.timestamp() - total_seconds
        )
        assert out == expected_timestamp

    @raises(MissingMandatoryParamError)
    def test_get_timestamp_in_seconds_invalid(self):
        """
        Tests that get_timestamp_in_seconds method works expectedly - with invalid inputs - all 0
        method should raise an error - we should expect at least one non-zero param
        """
        TimeUtils.get_timestamp_in_seconds(days=0, hours=0, minutes=0, seconds=0)

    @parameterized.expand(
        [
            (
                "no inputs",
                0,
                0,
                0,
                0,
                datetime(2023, 6, 4, 10, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
            ),
            (
                "with inputs",
                1,
                2,
                30,
                45,
                datetime(2023, 6, 3, 7, 59, 15).strftime("%Y-%m-%dT%H:%M:%SZ"),
            ),
        ]
    )
    @patch("openstack_query.time_utils.TimeUtils.get_current_time")
    def test_convert_to_timestamp(
        self,
        name,
        days,
        hours,
        minutes,
        seconds,
        expected_timestamp,
        mock_current_datetime,
    ):
        """
        Tests that convert_to_timestamp method works expectedly
        method takes a set of integer params "days, hours, minutes, seconds" and calculates a relative timestamp
        of that many seconds in the past from current time
        """
        mock_current_datetime.return_value = datetime(2023, 6, 4, 10, 30, 0)
        out = TimeUtils.convert_to_timestamp(days, hours, minutes, seconds)
        mock_current_datetime.assert_called_once()
        self.assertEqual(out, expected_timestamp)
