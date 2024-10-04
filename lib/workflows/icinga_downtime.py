from datetime import datetime

import pytz

from structs.icinga.downtime_details import DowntimeDetails
from structs.icinga.icinga_account import IcingaAccount

from icinga_api import downtime


def schedule_downtime(
    icinga_account: IcingaAccount,
    object_type: str,
    name: str,
    start_time: str,
    duration: int,
    comment: str,
    is_fixed: bool,
):

    # Local UK time to Unix timestamp
    datetime_object = datetime.strptime(start_time, "%d/%m/%y %H:%M:%S")

    uk_timezone = pytz.timezone("Europe/London")
    local_time = uk_timezone.localize(datetime_object)
    utc_time = local_time.astimezone(pytz.utc)
    unix_timestamp = int(utc_time.timestamp())

    downtime_details = DowntimeDetails(
        object_type=object_type,
        object_name=name,
        start_time=unix_timestamp,
        duration=duration,
        comment=comment,
        is_fixed=is_fixed,
    )

    downtime.schedule_downtime(icinga_account=icinga_account, details=downtime_details)


def remove_downtime(icinga_account: IcingaAccount, object_type: str, name: str):

    downtime.remove_downtime(
        icinga_account=icinga_account,
        object_type=object_type,
        object_name=name,
    )
