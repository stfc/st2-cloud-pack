import datetime as dt
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
) -> None:
    """
    Action to run after a successful reboot

    :param alertmanager_account: Alertmanager Account to use
    :type alertmanager_account: AlertManagerAccount datclass object
    :param hypervisor_hostname: the name of the hypervisor
    :type hypervisor_hostname: str
    :param conn: Openstack Connection
    :type conn: openstack.connection.Connection

    return: None
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
        date = dt.datetime.now(dt.timezone.utc).date().isoformat()
        disable_service(
            conn=conn,
            hypervisor_name=hypervisor_hostname,
            service_binary="nova-compute",
            disabled_reason=f"{date} - Failed to schedule after patching - ST2",
        )
        raise exc
    silences = get_hv_silences(alertmanager_account, hypervisor_hostname)
    for silence in silences:
        details = silences[silence]["details"]
        new_details = SilenceDetails(
            matchers=details.matchers,
            author="stackstorm",
            start_time_dt=dt.datetime.now(dt.timezone.utc),
            comment="Stackstorm: HV Patched",
            duration_hours=3,
        )

        update_silence(alertmanager_account, silence, new_details)
