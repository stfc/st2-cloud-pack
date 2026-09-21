import datetime


def _timestamp_today() -> str:
    """
    return a timestamp for the current time in UTC
    """
    n = datetime.datetime.utcnow()
    return n.strftime("%Y-%m-%d")
