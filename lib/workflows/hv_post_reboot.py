from enums.icinga.icinga_objects import IcingaObject
from structs.alertmanager.alertmanager_account import AlertManagerAccount

from structs.icinga.icinga_account import IcingaAccount
from alertmanager_api.silence import AlertManagerAPI

# from alertmanager_api.silence_details import SilenceDetails
from icinga_api import downtime


def post_reboot(icinga_account: IcingaAccount, name: str):
    """
    Action to run after a successful reboot
    :param icinga_account: Icinga account to use
    :param name: Name of host in icinga
    """
    # Remove downtime
    downtime.remove_downtime(
        icinga_account=icinga_account,
        object_type=IcingaObject.HOST,
        object_name=name,
    )
    # get silence to be removed
    alertmanager_account = AlertManagerAccount(
        username="stackstorm", password="password", alertmanager_endpoint="endpoint"
    )
    alert_manager = AlertManagerAPI(alertmanager_account)
    silence = alert_manager.get_silences()
    try:
        alert_manager.remove_silence(silence)
        print(f"Silence with ID {silence.silence_id} has been removed successfully.")
    except Exception as e:
        print(f"Failed to remove silence: {e}")

    # Remove alertmanager silence
    # test vm creation
    # enable in openstack
