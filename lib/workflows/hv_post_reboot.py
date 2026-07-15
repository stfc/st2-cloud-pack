from openstack.connection import Connection

from apis.openstack_api.openstack_service import enable_service
from apis.alertmanager_api.silence import get_hv_silences, remove_silence
from apis.alertmanager_api.structs.alertmanager_account import AlertManagerAccount
from workflows.hv_create_test_server import create_test_server


def post_reboot(
    alertmanager_account: AlertManagerAccount,
    hypervisor_hostname: str,
    conn: Connection,
):
    """
    Action to run after a successful reboot
    :param icinga_account: Icinga account to use
    :param hypervisor_hostname: Hostname of hypervisor to run action against
    :param alertmanager_account: Alertmanager Account to use
    :param conn: Openstack Connection
    """
    enable_service(
        conn=conn, hypervisor_name=hypervisor_hostname, service_binary="nova-compute"
    )
    create_test_server(
        conn=conn,
        hypervisor_names=hypervisor_hostname,
        test_all_flavors=False,
        delete_on_failure=True,
    )
    silences = get_hv_silences(alertmanager_account, hypervisor_hostname)
    for silence_id in silences:
        remove_silence(alertmanager_account, silence_id)
