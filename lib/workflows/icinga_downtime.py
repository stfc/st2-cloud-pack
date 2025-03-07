from datetime import datetime
from typing import Optional

import pytz

from enums.icinga.icinga_objects import IcingaObject
from structs.icinga.downtime_details import DowntimeDetails
from structs.icinga.icinga_account import IcingaAccount

from icinga_api import downtime


# pylint:disable=too-many-locals
def schedule_downtime(
    icinga_account: IcingaAccount,
    object_type: str,
    name: str,
    start_time: str,
    end_time: str,
    comment: str,
    is_fixed: bool,
    duration: Optional[int] = None,
):
    # Local UK time to Unix timestamp
    start_datetime = datetime.strptime(start_time, "%d/%m/%y %H:%M:%S")
    end_datetime = datetime.strptime(end_time, "%d/%m/%y %H:%M:%S")

    uk_timezone = pytz.timezone("Europe/London")
    local_start_time = uk_timezone.localize(start_datetime)
    local_end_time = uk_timezone.localize(end_datetime)
    utc_start_time = local_start_time.astimezone(pytz.utc)
    utc_end_time = local_end_time.astimezone(pytz.utc)
    start_timestamp = int(utc_start_time.timestamp())
    end_timestamp = int(utc_end_time.timestamp())

    downtime_details = DowntimeDetails(
        object_type=IcingaObject[object_type.upper()],
        object_name=name,
        start_time=start_timestamp,
        end_time=end_timestamp,
        duration=duration if not is_fixed else (end_timestamp - start_timestamp),
        comment=comment,
        is_fixed=is_fixed,
    )

    downtime.schedule_downtime(icinga_account=icinga_account, details=downtime_details)


def remove_downtime(icinga_account: IcingaAccount, object_type: str, name: str):
    downtime.remove_downtime(
        icinga_account=icinga_account,
        object_type=IcingaObject[object_type.upper()],
        object_name=name,
    )
