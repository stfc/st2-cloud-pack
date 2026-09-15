from datetime import datetime, timezone


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
