from datetime import datetime, timedelta


def convert_to_timestamp(
    self,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: float = 0,
    timestamp_fmt: str = "%Y-%m-%dT%H:%M:%SZ",
):
    delta = self._get_timestamp_in_seconds(days, hours, minutes, seconds)
    return (datetime(1970, 1, 1) + timedelta(seconds=delta)).strftime(timestamp_fmt)
