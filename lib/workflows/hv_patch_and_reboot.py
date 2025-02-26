import datetime

from alertmanager_api.silence import remove_silence, schedule_silence

from paramiko import SSHException
from enums.icinga.icinga_objects import IcingaObject
from icinga_api.downtime import schedule_downtime, remove_downtime
from structs.alertmanager.alert_matcher_details import AlertMatcherDetails
from structs.alertmanager.alertmanager_account import AlertManagerAccount
from structs.alertmanager.silence_details import SilenceDetails
from structs.icinga.downtime_details import DowntimeDetails
from structs.icinga.icinga_account import IcingaAccount
from structs.ssh.ssh_connection_details import SSHDetails
from ssh_api.exec_command import SSHConnection


# pylint:disable=too-many-locals
def patch_and_reboot(
    alertmanager_account: AlertManagerAccount,
    icinga_account: IcingaAccount,
    hypervisor_name: str,
    private_key_path: str,
) -> None:
    """
    Takes the selected hypervisor, schedules a downtime on it starting immediately then runs
    the patch and reboot scripts on the machine, before ending the downtime.
    :param alertmanager_account: Alertmanager Account to use
    :param icinga_account: IcingaAccount: The icinga account object to use to schedule and remove the downtimes
    :param hypervisor_name: the name of the hypervisor - should also be the host name on icinga
    :param private_key_path: Path to the stackstorm key
    return: None
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
    matcher_instance = AlertMatcherDetails(name="instance", value=hypervisor_name)
    silence_details_instance = SilenceDetails(
        matchers=[matcher_instance],
        author="stackstorm",
        comment="Stackstorm HV maintenance",
        start_time_dt=datetime.datetime.utcnow(),
        duration_hours=6,
    )
    scheduled_silence_id_instance = schedule_silence(
        alertmanager_account, silence_details_instance
    )
    matcher_hostname = AlertMatcherDetails(name="hostname", value=hypervisor_name)
    silence_details_hostname = SilenceDetails(
        matchers=[matcher_hostname],
        author="stackstorm",
        comment="Stackstorm HV maintenance",
        start_time_dt=datetime.datetime.utcnow(),
        duration_hours=6,
    )
    scheduled_silence_id_hostname = schedule_silence(
        alertmanager_account, silence_details_hostname
    )
    try:
        ssh_client.run_command_on_host("patch")
        ssh_client.run_command_on_host("reboot")
    except SSHException as exc:
        remove_downtime(
            icinga_account=icinga_account,
            object_type=IcingaObject.HOST,
            object_name=hypervisor_name,
        )
        remove_silence(alertmanager_account, scheduled_silence_id_instance)
        remove_silence(alertmanager_account, scheduled_silence_id_hostname)
        raise exc
