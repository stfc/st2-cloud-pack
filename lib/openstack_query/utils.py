from datetime import datetime, timedelta


def convert_to_timestamp(
    self,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: float = 0,
    timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ",
):
    """
    Helper function to convert a relative time from current time into a timestamp
    :param days: (Optional) relative number of days since current time
    :param hours: (Optional) relative number of hours since current time
    :param minutes: (Optional) relative number of minutes since current time
    :param seconds: (Optional) relative number of seconds since current time
    :param timestamp_fmt: (Optional) timestamp format of result (default: yyyy-MM-ddTHH:mm:ssZ)
    """
    delta = self._get_timestamp_in_seconds(days, hours, minutes, seconds)
    return (datetime(1970, 1, 1) + timedelta(seconds=delta)).strftime(timestamp_fmt)
