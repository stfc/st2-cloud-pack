from openstack.connection import Connection
from openstack.exceptions import ResourceFailure

from apis.openstack_api.openstack_service import enable_service
from apis.openstack_api.openstack_service import disable_service
from apis.alertmanager_api.structs.silence_details import SilenceDetails
from apis.alertmanager_api.silence import get_hv_silences, update_silence
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
    try:
        create_test_server(
            conn=conn,
            hypervisor_names=hypervisor_hostname,
            test_all_flavors=False,
            delete_on_failure=True,
        )
    except ResourceFailure as exc:
        disable_service(
            conn=conn,
            hypervisor_name=hypervisor_hostname,
            service_binary="nova-compute",
            disabled_reason="Failed to schedule after patching",
        )
        raise exc
    silences = get_hv_silences(alertmanager_account, hypervisor_hostname)
    for silence in silences:
        details = silences[silence]["details"]
        new_details = SilenceDetails(
            matchers=details.matchers,
            author="stackstorm",
            start_time_dt=details.start_time_dt,
            comment="Stackstorm: HV Patched",
            duration_hours=3,
        )

        update_silence(alertmanager_account, silence, new_details)
