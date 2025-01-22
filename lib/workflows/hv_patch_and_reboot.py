import datetime

from paramiko import SSHException
from enums.icinga.icinga_objects import IcingaObject
from icinga_api.downtime import schedule_downtime, remove_downtime
from structs.icinga.downtime_details import DowntimeDetails
from structs.icinga.icinga_account import IcingaAccount
from structs.ssh.ssh_connection_details import SSHDetails
from ssh_api.exec_command import SSHConnection


def patch_and_reboot(
    icinga_account: IcingaAccount,
    hypervisor_name: str,
    private_key_path: str,
) -> dict:
    """
    Takes the selected hypervisor, schedules a downtime on it starting immediately then runs
    the patch and reboot scripts on the machine, before ending the downtime.
    icinga_account: IcingaAccount: The icinga account object to use to schedule and remove the downtimes
    hypervisor_name: the name of the hypervisor - should also be the host name on icinga
    return: Dict[str] a dictionary containing the remote commands output
    """
    connection_details = SSHDetails(
        host=hypervisor_name, username="stackstorm", private_key_path=private_key_path
    )
    ssh_client = SSHConnection(connection_details)
    start_time = datetime.datetime.utcnow()
    end_time = start_time + datetime.timedelta(hours=6)
    start_timestamp = int(start_time.timestamp())
    end_timestamp = int(end_time.timestamp())
    downtime_details = DowntimeDetails(
        object_type=IcingaObject.HOST,
        object_name=hypervisor_name,
        start_time=start_timestamp,
        end_time=end_timestamp,
        comment=f"starting downtime to patch and reboot host: {hypervisor_name}",
        is_fixed=True,
        duration=end_timestamp - start_timestamp,
    )
    schedule_downtime(icinga_account=icinga_account, details=downtime_details)
    try:
        patch_out = ssh_client.run_command_on_host("patch")
        reboot_out = ssh_client.run_command_on_host("reboot")
        return {
            "patch_output": patch_out.decode(),
            "reboot_output": reboot_out.decode(),
        }
    except SSHException as exc:
        remove_downtime(
            icinga_account=icinga_account,
            object_type=IcingaObject.HOST,
            object_name=hypervisor_name,
        )
        raise exc
