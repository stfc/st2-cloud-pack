from workflows.icinga_downtime import schedule_downtime
from structs.icinga.icinga_account import IcingaAccount
from workflows.icinga_downtime import remove_downtime


def patch_and_reboot(
    icinga_account: IcingaAccount,
    name: str,
    start_time: str,
    end_time: str,
):
    comment = f"starting downtime to patch and reboot host: {name}"
    res = schedule_downtime(
        icinga_account=icinga_account,
        object_type="Host",
        name=name,
        start_time=start_time,
        end_time=end_time,
        is_fixed=True,
        comment=comment,
    )
    return res
