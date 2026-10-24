from apis.wazuh_api.wazuh_query_agents import wazuh_list_all_servers
from apis.openstack_api.openstack_server import (
    get_all_servers,
    shutoff_server,
    admin_lock_server,
)
from apis.utils.diff_utils import compare_2_lists


def shutoff_all_non_wazuh_servers(conn, wazuh_account, admin_lock: bool) -> None:
    """
    set all OpenStack Servers not reporting to Wazuh in SHUTOFF
    Also, is the boolean admin_lock is True, lock them so
    users cannot reactivate them
    """
    all_openstack_servers = get_all_servers(conn)
    all_wazuh_servers = wazuh_list_all_servers(wazuh_account)
    only_in_openstack, _, _ = compare_2_lists(all_openstack_servers, all_wazuh_servers)
    for server_id in only_in_openstack:
        shutoff_server(conn, server_id)
        if admin_lock:
            admin_lock_server(conn, server_id, "Server is not reporting to Wazuh")
