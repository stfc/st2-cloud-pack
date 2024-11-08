from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from workflows.icinga_downtime import schedule_downtime, remove_downtime
from workflows.ssh_remote_command import ssh_remote_command

from structs.icinga.icinga_account import IcingaAccount

from paramiko.ssh_exception import SSHException


def patch_and_reboot(
    icinga_account: IcingaAccount,
    name: str,
    start_time: str,
    end_time: str,
    host: str,
    private_key_path: str,
):
    comment = f"starting downtime to patch and reboot host: {name}"
    downtime_scheduled = False
    try:
        schedule_downtime(
            icinga_account=icinga_account,
            object_type="Host",
            name=name,
            start_time=start_time,
            end_time=end_time,
            is_fixed=True,
            comment=comment,
        )
        downtime_scheduled = True
        patch_out = ssh_remote_command(
            host=host,
            username="stackstorm",
            private_key_path=private_key_path,
            command=f"{host} patch",
        )
        reboot_out = ssh_remote_command(
            host=host,
            username="stackstorm",
            private_key_path=private_key_path,
            command=f"{host} reboot",
        )
    except SSHException as exc:
        raise SSHException("SSH command failed during patch or reboot") from exc
    except MissingMandatoryParamError as exc:
        raise MissingMandatoryParamError("A required parameter is missing") from exc
    finally:
        if downtime_scheduled:
            remove_downtime(
                icinga_account=icinga_account,
                object_type="Host",
                name=name,
            )
    return {"patch_output": patch_out, "reboot_output": reboot_out}
