from datetime import datetime, timedelta
import re
import pytz

from apis.icinga_api.downtime import schedule_downtime
from apis.icinga_api.enums.icinga_objects import IcingaObject
from apis.icinga_api.structs.downtime_details import DowntimeDetails
from apis.icinga_api.structs.icinga_account import IcingaAccount

from apis.alertmanager_api.silence import schedule_silence
from apis.alertmanager_api.structs.alert_matcher_details import AlertMatcherDetails
from apis.alertmanager_api.structs.alertmanager_account import AlertManagerAccount
from apis.alertmanager_api.structs.silence_details import SilenceDetails


def get_number_of_hours(start_dt, end_time_str, duration):
    """
    Get the total number of hours between a start time and an end time

    :param start_dt: start date
    :type start_dt: datetime object

    :param end_time_str: a datetime string in format "YYYY-MM-DD HH:MM"
    :type end_time_str: str

    :param duration: a duration string like "5d 12h", "3d", "24h", etc.
    :type duration: str

    :return: the number of hours to end date
    :rtype: int

    :raises ValueError: if the input string is invalid or contains negative values
    """
    if end_time_str is not None:
        end_time_str = end_time_str.strip()
    if duration is not None:
        duration = duration.strip()
    if not end_time_str and not duration:
        raise ValueError("Input strings cannot be both empty at the same time")

    if end_time_str and duration:
        raise ValueError("Input strings cannot be both valid at the same time")

    if end_time_str:
        return _get_number_of_hours_from_absolute_datetime(start_dt, end_time_str)

    if duration:
        return _get_number_of_hours_from_duration(duration)

    # if we are still here is because no return statement has been issued
    # meaning the input did not match any of the valid formats
    raise ValueError(
        "Invalid input format. Expected either 'YYYY-MM-DD HH:MM' "
        f"or duration format like '5d', '12h', '2d 6h'. Got: '{end_time_str}'"
    )


def _get_number_of_hours_from_absolute_datetime(start_dt, datetime_str):
    """
    Get the total number of hours from a start time and an end time

    :param start_dt: start time
    :type start_dt: datetime object

    :param datetime_str: datetime string in format "YYYY-MM-DD HH:MM"
    :type end_time_str: str

    :return: the number of hours to end date
    :rtype: int

    :raises ValueError: if the input string is invalid
    :raises ValueError: if the end date is earlier that start date
    """
    try:
        end_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M").replace(
            tzinfo=pytz.utc
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid datetime format. Expected 'YYYY-MM-DD HH:MM', got '{datetime_str}'"
        ) from exc
    if start_dt >= end_dt:
        raise ValueError("end time cannot be earlier than now")
    duration = end_dt - start_dt
    # Convert total seconds to hours
    hours = int(duration.total_seconds() / 3600)
    return hours


def _get_number_of_hours_from_duration(duration_str):
    """
    Get the total number of hours from a duration string

    :param duration_str: duration string like "5d 12h", "3d", "24h", etc.
    :type duration_str: str

    :return: the number of hours to end date
    :rtype: int

    :raises ValueError: if the input string has wrong format
    """
    duration_str = duration_str.strip()
    # Check for negative signs
    if "-" in duration_str:
        raise ValueError(
            "Negative durations are not allowed. Only positive numbers are permitted."
        )

    days = 0
    hours = 0

    # Search for days pattern
    days_match = re.search(r"(\d+)d", duration_str, re.IGNORECASE)
    if days_match:
        days = int(days_match.group(1))

    # Search for hours pattern
    hours_match = re.search(r"(\d+)h", duration_str, re.IGNORECASE)
    if hours_match:
        hours = int(hours_match.group(1))

    # Validate that at least one unit was found
    if days == 0 and hours == 0:
        raise ValueError(
            f"Invalid duration format. Expected format like '5d', '12h', or '2d 6h', got '{duration_str}'"
        )

    total_hours = days * 24 + hours
    return total_hours


# pylint:disable=too-many-locals
def schedule_hypervisor_downtime(
    icinga_account: IcingaAccount,
    alertmanager_account: AlertManagerAccount,
    hypervisor_name: str,
    comment: str,
    end_time: str,
    duration: str,
    set_silence: bool,
    set_downtime: bool,
):

    # Local UK time to Unix timestamp
    start_datetime = datetime.now(pytz.utc)
    duration_hours = get_number_of_hours(start_datetime, end_time, duration)
    end_datetime = start_datetime + timedelta(hours=duration_hours)

    start_timestamp = int(start_datetime.timestamp())
    end_timestamp = int(end_datetime.timestamp())

    downtime_details = DowntimeDetails(
        object_type=IcingaObject["HOST"],
        object_name=hypervisor_name,
        start_time=start_timestamp,
        end_time=end_timestamp,
        duration=(end_timestamp - start_timestamp),
        comment=comment,
        is_fixed=True,
    )
    matcher_instance = AlertMatcherDetails(name="instance", value=hypervisor_name)
    matcher_hostname = AlertMatcherDetails(name="hostname", value=hypervisor_name)

    silence_details_instance = SilenceDetails(
        matchers=[matcher_instance],
        author="stackstorm",
        comment=comment,
        start_time_dt=start_datetime,
        duration_hours=duration_hours,
    )
    silence_details_hostname = SilenceDetails(
        matchers=[matcher_hostname],
        author="stackstorm",
        comment=comment,
        start_time_dt=start_datetime,
        duration_hours=duration_hours,
    )

    if set_silence:
        schedule_silence(alertmanager_account, silence_details_instance)
        schedule_silence(alertmanager_account, silence_details_hostname)
    if set_downtime:
        schedule_downtime(icinga_account=icinga_account, details=downtime_details)
