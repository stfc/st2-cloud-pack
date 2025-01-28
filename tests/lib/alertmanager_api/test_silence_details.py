import unittest
from datetime import datetime, timezone
from alertmanager_api.silence_details import SilenceDetails


class TestSilenceDetails(unittest.TestCase):
    def convert_utc_string_to_datetime(self, datetime_string):
        """
        Converts a UTC datetime string to a datetime object with timezone information.

        :param datetime_string: A string in the format "2025-01-01T12:00:00"
        :return: A datetime object with UTC timezone
        """
        naive_datetime = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S")
        return naive_datetime.replace(tzinfo=timezone.utc)

    def test_start_time_str(self):
        """
        use case: validate the returned value of start_time has the right format
        """
        start_time = self.convert_utc_string_to_datetime("2025-01-01T12:00:00")
        silence = SilenceDetails(start_time_dt=start_time)
        expected_start_time_str = "2025-01-01T12:00:00Z"
        self.assertEqual(silence.start_time_str, expected_start_time_str)

    def test_end_time_str(self):
        """
        use case: validate the returned value of end_time has the right format
        """
        end_time = self.convert_utc_string_to_datetime("2025-01-01T12:00:00")
        silence = SilenceDetails(end_time_dt=end_time)
        expected_end_time_str = "2025-01-01T12:00:00Z"
        self.assertEqual(silence.end_time_str, expected_end_time_str)
