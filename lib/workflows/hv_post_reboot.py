from openstack.connection import Connection
from alertmanager_api.silence import AlertManagerAPI

from enums.icinga.icinga_objects import IcingaObject
from structs.alertmanager.alertmanager_account import AlertManagerAccount
from structs.icinga.icinga_account import IcingaAccount
from hv_service_actions import hv_service_enable
from icinga_api import downtime


def post_reboot(icinga_account: IcingaAccount, name: str, conn=Connection):
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

    # get silence to be removed and remove the alertmanager silence
    # alertmanager_account = AlertManagerAccount(
    #     username="stackstorm", password="password", alertmanager_endpoint="endpoint"
    # )
    # alert_manager = AlertManagerAPI(alertmanager_account)
    # silences = alert_manager.get_silences().get_by_name(name)
    # alert_manager.remove_silences(silences)
    # test vm creation

    # enable in openstack
    hv_service_enable(conn=conn, hypervisor_name=name, service_binary="nova-compute")
