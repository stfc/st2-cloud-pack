from datetime import datetime
from typing import Optional

import pytz

from alertmanager_api.silence import schedule_silence
from enums.icinga.icinga_objects import IcingaObject
from structs.alertmanager.alert_matcher_details import AlertMatcherDetails
from structs.alertmanager.alertmanager_account import AlertManagerAccount
from structs.alertmanager.silence_details import SilenceDetails
from structs.icinga.downtime_details import DowntimeDetails
from structs.icinga.icinga_account import IcingaAccount

from icinga_api import downtime


# pylint:disable=too-many-locals
def schedule_hypervisor_downtime(
    icinga_account: IcingaAccount,
    alertmanager_account: AlertManagerAccount,
    hypervisor_name: str,
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
        object_type=IcingaObject["HOST"],
        object_name=hypervisor_name,
        start_time=start_timestamp,
        end_time=end_timestamp,
        duration=duration if not is_fixed else (end_timestamp - start_timestamp),
        comment=comment,
        is_fixed=is_fixed,
    )
    matcher_instance = AlertMatcherDetails(name="instance", value=hypervisor_name)
    matcher_hostname = AlertMatcherDetails(name="hostname", value=hypervisor_name)

    silence_details_instance = SilenceDetails(
        matchers=[matcher_instance],
        author="stackstorm",
        comment=comment,
        start_time_dt=utc_start_time,
        duration_hours=duration if not is_fixed else (end_timestamp - start_timestamp),
    )
    silence_details_hostname = SilenceDetails(
        matchers=[matcher_hostname],
        author="stackstorm",
        comment=comment,
        start_time_dt=utc_start_time,
        duration_hours=duration if not is_fixed else (end_timestamp - start_timestamp),
    )

    schedule_silence(alertmanager_account, silence_details_instance)
    schedule_silence(alertmanager_account, silence_details_hostname)

    downtime.schedule_downtime(icinga_account=icinga_account, details=downtime_details)
