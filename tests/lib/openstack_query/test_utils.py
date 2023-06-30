import unittest
from datetime import datetime

from unittest.mock import MagicMock, patch, call
from parameterized import parameterized
from nose.tools import raises

import openstack_query.utils as utils
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError


class UtilsTests(unittest.TestCase):
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
    @patch("openstack_query.utils.get_current_time")
    def test_get_timestamp_in_seconds(
        self, name, days, hours, minutes, seconds, total_seconds, mock_current_datetime
    ):
        mock_current_datetime.return_value = datetime(2023, 6, 4, 10, 30, 0)
        out = utils.get_timestamp_in_seconds(days, hours, minutes, seconds)

        mock_current_datetime.assert_called_once()

        expected_timestamp = (
            mock_current_datetime.return_value.timestamp() - total_seconds
        )
        assert out == expected_timestamp

    @raises(MissingMandatoryParamError)
    def test_get_timestamp_in_seconds_invalid(self):
        utils.get_timestamp_in_seconds(days=0, hours=0, minutes=0, seconds=0)

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
                datetime(2023, 6, 3, 6, 59, 15).strftime("%Y-%m-%dT%H:%M:%SZ"),
            ),
        ]
    )
    @patch("openstack_query.utils.get_current_time")
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
        mock_current_datetime.return_value = datetime(2023, 6, 4, 10, 30, 0)
        out = utils.convert_to_timestamp(days, hours, minutes, seconds)
        mock_current_datetime.assert_called_once()
        self.assertEqual(out, expected_timestamp)
