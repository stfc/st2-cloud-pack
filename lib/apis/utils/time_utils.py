from datetime import datetime


def timestamp_today() -> str:
    """
    return a timestamp for the current time in UTC
    """
    n = datetime.utcnow()
    return n.strftime("%Y-%m-%d")


def days_since_timestamp(timestamp: str) -> int:
    """
    returns the number of days since a given date
    pass as a timestamp with format "%Y-%m-%d"
    """
    try:
        date = datetime.strptime(timestamp, "%Y-%m-%d")
    except (ValueError, TypeError) as e:
        raise ValueError("timestamp must have format YYYY-MM-DD") from e

    return (datetime.utcnow() - date).days
