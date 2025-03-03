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
    hypervisor_hostname: str,
    conn=Connection,
):
    """
    Action to run after a successful reboot
    :param icinga_account: Icinga account to use
    :param hypervisor_hostname: Hostname of hypervisor to run action against
    :param alertmanager_account: Alertmanager Account to use
    :param conn: Openstack Connection
    """
    downtime.remove_downtime(
        icinga_account=icinga_account,
        object_type=IcingaObject.HOST,
        object_name=hypervisor_hostname,
    )
    hv_service_enable(
        conn=conn, hypervisor_name=hypervisor_hostname, service_binary="nova-compute"
    )
    create_test_server(
        conn=conn,
        hypervisor_name=hypervisor_hostname,
        test_all_flavors=False,
        delete_on_failure=True,
    )
    silences = get_hv_silences(alertmanager_account, hypervisor_hostname)
    for silence_id in silences:
        remove_silence(alertmanager_account, silence_id)
