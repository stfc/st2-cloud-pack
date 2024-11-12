import datetime

from icinga_api.downtime import schedule_downtime, remove_downtime
from structs.icinga.downtime_details import DowntimeDetails
from structs.icinga.icinga_account import IcingaAccount
from structs.ssh.ssh_connection_details import SSHDetails
from ssh_api.exec_command import SSHConnection


def patch_and_reboot(
    icinga_account: IcingaAccount,
    name: str,
    host: str,
    private_key_path: str,
):
    connection_details = SSHDetails(
        host=host, username="stackstorm", private_key_path=private_key_path
    )
    ssh_client = SSHConnection(connection_details)
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(hours=6)
    start_timestamp = int(start_time.timestamp())
    end_timestamp = int(end_time.timestamp())
    downtime_details = DowntimeDetails(
        object_type="Host",
        object_name=name,
        start_time=start_timestamp,
        end_time=end_timestamp,
        comment=f"starting downtime to patch and reboot host: {name}",
        is_fixed=True,
        duration=end_timestamp - start_timestamp,
    )
    schedule_downtime(icinga_account=icinga_account, details=downtime_details)
    try:
        patch_out = ssh_client.run_command_on_host("patch").decode()
        reboot_out = ssh_client.run_command_on_host("reboot").decode()

    finally:
        remove_downtime(
            icinga_account=icinga_account,
            object_type="Host",
            object_name=name,
        )
    return {"patch_output": patch_out, "reboot_output": reboot_out}
