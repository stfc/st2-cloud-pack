import datetime as dt

from paramiko import SSHException

from apis.alertmanager_api.silence import remove_silence, schedule_silence
from apis.alertmanager_api.structs.alert_matcher_details import AlertMatcherDetails
from apis.alertmanager_api.structs.alertmanager_account import AlertManagerAccount
from apis.alertmanager_api.structs.silence_details import SilenceDetails

from apis.ssh_api.structs.ssh_connection_details import SSHDetails
from apis.ssh_api.exec_command import SSHConnection


# pylint:disable=too-many-locals
def patch_and_reboot(
    alertmanager_account: AlertManagerAccount,
    hypervisor_name: str,
    private_key_path: str,
) -> None:
    """
    Takes the selected hypervisor, schedules a downtime on it starting immediately then runs
    the patch and reboot scripts on the machine, before ending the downtime.

    :param alertmanager_account: Alertmanager Account to use
    :type alertmanager_account: AlertManagerAccount datclass object
    :param hypervisor_name: the name of the hypervisor
    :type hypervisor_name: str
    :param private_key_path: Path to the stackstorm private key for ssh connections
    :type private_key_path: str

    return: None
    """
    connection_details = SSHDetails(
        host=hypervisor_name, username="stackstorm", private_key_path=private_key_path
    )
    ssh_client = SSHConnection(connection_details)
    matcher_instance = AlertMatcherDetails(name="instance", value=hypervisor_name)

    start_time_dt = dt.datetime.now(dt.timezone.utc)
    weekday = start_time_dt.weekday()

    # Set the silences to a fixed end time of 10:10am
    # If starting patching on a Friday(4) or Saturday(5) set
    # the silence to expire on the following Monday
    if weekday in [4, 5]:
        delta = dt.timedelta(days=7 - weekday)
        end_date = start_time_dt + delta
        end_time_dt = end_date.replace(hour=10, minute=10)
    else:
        delta = dt.timedelta(days=1)
        end_date = start_time_dt + delta
        end_time_dt = end_date.replace(hour=10, minute=10)

    silence_details_instance = SilenceDetails(
        matchers=[matcher_instance],
        author="stackstorm",
        comment="Stackstorm: HV Patching",
        start_time_dt=start_time_dt,
        end_time_dt=end_time_dt,
    )
    scheduled_silence_id_instance = schedule_silence(
        alertmanager_account, silence_details_instance
    )
    matcher_hostname = AlertMatcherDetails(name="hostname", value=hypervisor_name)
    silence_details_hostname = SilenceDetails(
        matchers=[matcher_hostname],
        author="stackstorm",
        comment="Stackstorm: HV Patching",
        start_time_dt=start_time_dt,
        end_time_dt=end_time_dt,
    )
    scheduled_silence_id_hostname = schedule_silence(
        alertmanager_account, silence_details_hostname
    )
    try:
        ssh_client.run_command_on_host("patch")
        ssh_client.run_command_on_host("reboot")
    except SSHException as exc:
        remove_silence(alertmanager_account, scheduled_silence_id_instance)
        remove_silence(alertmanager_account, scheduled_silence_id_hostname)
        raise exc
