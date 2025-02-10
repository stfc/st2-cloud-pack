from openstack.connection import Connection

from alertmanager_api.silence import get_hv_silences, remove_silence

from enums.icinga.icinga_objects import IcingaObject

from structs.alertmanager.alertmanager_account import AlertManagerAccount
from structs.icinga.icinga_account import IcingaAccount
from workflows.hv_service_actions import hv_service_enable
from workflows.hv_create_test_server import create_test_server
from icinga_api import downtime


def post_reboot(
    alertmanager_account: AlertManagerAccount,
    icinga_account: IcingaAccount,
    name: str,
    conn=Connection,
):
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
    # get silence to be removed and remove all the alertmanager silences on that host.
    silences = get_hv_silences(alertmanager_account, name)
    for silence_id in silences:
        remove_silence(alertmanager_account, silence_id)
    # test vm creation
    create_test_server(conn=conn, hypervisor_name=name, test_all_flavors=False)
    # enable in openstack
    hv_service_enable(conn=conn, hypervisor_name=name, service_binary="nova-compute")
