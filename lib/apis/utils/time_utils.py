from datetime import datetime, timedelta, timezone


def parse_iso_utc(value: str) -> datetime:
    """
    Handles the 'Z' suffix, as datetime.fromisoformat only accepts this
    in Python 3.11+, so we need to drop it

    :param value: the ISO 8601 timestamp
    :return: a sanitised UTC datetime
    :raises ValueError: if the value is not a valid ISO 8601 timestamp
    """
    if value.endswith(("Z", "z")):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def timestamp_today() -> str:
    """
    return a timestamp for the current time in UTC
    """
    n = datetime.now(timezone.utc)
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

    return (datetime.now(timezone.utc) - date).days


def calc_wed_maint_next_week():
    """
    returns the next week's Wednesday maintenance date
    """
    today = datetime.now(timezone.utc)
    days_ahead = 2 - today.weekday()  # Wednesday is 2
    days_ahead += 7
    next_wednesday = today + timedelta(days=days_ahead)
    return next_wednesday.strftime("%Y-%m-%d")
