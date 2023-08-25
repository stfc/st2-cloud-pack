import unittest
from unittest.mock import patch

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from openstack_query.time_utils import TimeUtils


# pylint:disable=too-many-arguments


class TimeUtilsTests(unittest.TestCase):
    """
    Runs various tests to ensure that utils module functions expectedly
    """

    def test_get_timestamp_in_seconds(self):
        """
        Tests that get_timestamp_in_seconds method works expectedly
        method takes a set of integer params "days, hours, minutes, seconds" and calculates total seconds
        """
        days, hours, minutes, seconds = 1, 2, 3, 4

        with patch("openstack_query.time_utils.datetime") as mock_datetime:
            with patch("openstack_query.time_utils.timedelta") as mock_timedelta:
                mock_datetime.now.return_value.timestamp.return_value = 6
                mock_timedelta.return_value.total_seconds.return_value = 2
                out = TimeUtils.get_timestamp_in_seconds(days, hours, minutes, seconds)

        # Now - amount of time in the past = expected out
        assert out == 4

        mock_datetime.now.assert_called_once()
        mock_datetime.now.return_value.timestamp.assert_called_once()

        mock_timedelta.assert_called_once_with(
            days=days, hours=hours, minutes=minutes, seconds=float(seconds)
        )
        mock_timedelta.return_value.total_seconds.assert_called()

    def test_get_timestamp_in_seconds_invalid(self):
        """
        Tests that get_timestamp_in_seconds method works expectedly - with invalid inputs - all 0
        method should raise an error - we should expect at least one non-zero param
        """
        with self.assertRaises(MissingMandatoryParamError):
            TimeUtils.get_timestamp_in_seconds(0, 0, 0, 0)
