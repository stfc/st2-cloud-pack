from datetime import datetime, timedelta

import pytz

from apis.alertmanager_api.silence import schedule_silence
from apis.icinga_api.downtime import schedule_downtime
from apis.icinga_api.enums.icinga_objects import IcingaObject
from apis.icinga_api.structs.downtime_details import DowntimeDetails
from apis.icinga_api.structs.icinga_account import IcingaAccount

from apis.alertmanager_api.structs.alert_matcher_details import AlertMatcherDetails
from apis.alertmanager_api.structs.alertmanager_account import AlertManagerAccount
from apis.alertmanager_api.structs.silence_details import SilenceDetails


# pylint:disable=too-many-locals
def schedule_hypervisor_downtime(
    icinga_account: IcingaAccount,
    alertmanager_account: AlertManagerAccount,
    hypervisor_name: str,
    comment: str,
    duration_hours: int,
    set_silence: bool,
    set_downtime: bool,
):

    # Local UK time to Unix timestamp
    start_datetime = datetime.now(pytz.utc)
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
