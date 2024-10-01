from datetime import datetime

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

    datetime_object = datetime.strptime(start_time, "%d/%m/%y %H:%M:%S")

    downtime_details = DowntimeDetails(
        object_type=object_type,
        object_name=name,
        start_time=datetime_object.timestamp(),
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
