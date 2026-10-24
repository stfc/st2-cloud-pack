import logging
from datetime import datetime, timedelta, timezone
from apis.wazuh_api.structs.wazuh_account import WazuhAccount
from apis.wazuh_api.wazuh_query_agents import wazuh_list_all_servers
from apis.openstack_api.openstack_server import (
    get_all_servers,
    shutoff_server,
    admin_lock_server,
)
from apis.openstack_api.openstack_project import get_project_id
from apis.utils.diff_utils import compare_2_lists
from apis.utils.read_config import read_config_file
from apis.openstack_api.openstack_event_list import EventList
from openstack.exceptions import NotFoundException, ResourceFailure, BadRequestException
from openstack.connection import Connection

logger = logging.getLogger(__name__)


def _shutoff_server(conn: Connection, server_id: str, admin_lock: bool) -> bool:
    """
    set a single OpenStack Server SHUTOFF
    Also, is the boolean admin_lock is True, lock it so
    users cannot reactivate them

    returns True if the Server was actually shutdown,
    otherwise returns False
    """
    logger.info("processing server_id %s", server_id)
    try:
        event_list = EventList(conn, server_id)
    except NotFoundException:
        logger.error(
            "unable to find Event List information for server_id %s, skipping it",
            server_id,
        )
        return False

    # Avoid "check-then-act" race condition:
    # it may happen that a VM just booted didn't have time yet to start
    # reporting to Wazuh. It shouldn't be set SHUTOFF just because of that.
    # To avoid it, we check if the VM has been in the latest status for at least
    # 60 minutes. If the status is ACTIVE, 60 minutes should be enough to
    # contact Wazuh. If the status is not ACTIVE, it doesn't matter as any attempt
    # to set it SHUTOFF will fail anyways.
    if datetime.now(timezone.utc) - event_list.last_event.date < timedelta(minutes=60):
        logger.info(
            "last event for server_id %s happened less than 60 minutes ago, skipping it",
            server_id,
        )
        return False

    try:
        shutoff_server(conn, server_id)
    except ResourceFailure:
        logger.error(
            "unable to SHUTOFF server_id %s, skipping it", server_id, exc_info=True
        )
        return False
    if admin_lock:
        try:
            admin_lock_server(
                conn,
                server_id,
                "Server is not compliant to our terms of service - Please raise a ticket to get unlocked",
            )
        except BadRequestException:
            logger.error(
                "unable to lock server_id %s, skipping it", server_id, exc_info=True
            )
    return True


def shutoff_all_non_wazuh_servers(
    conn: Connection, wazuh_account: WazuhAccount, admin_lock: bool
) -> bool:
    """
    set all OpenStack Servers not reporting to Wazuh in SHUTOFF
    Also, is the boolean admin_lock is True, lock them so
    users cannot reactivate them
    """
    logger.info("starting the process to SHUTOFF all servers not reporting to Wazuh")
    if admin_lock:
        logger.info("servers will also be admin locked")

    # 1. get the list of ACTIVE Servers not reporting to Wazuh
    all_openstack_servers = get_all_servers(conn, status="ACTIVE")
    all_wazuh_servers = wazuh_list_all_servers(wazuh_account)
    selected_list, _, _ = compare_2_lists(all_openstack_servers, all_wazuh_servers)

    # 2. remove the Load Balancers Amphorae from the list
    logger.info("we exclude the Load Balancer Amphorae from this operation")
    service_project_id = get_project_id(conn, "service")
    amphora_servers = get_all_servers(conn, service_project_id)
    logger.info("excluding %s Amphora servers", len(amphora_servers))
    selected_list, _, _ = compare_2_lists(selected_list, amphora_servers)

    # 3. remove the Servers listed in a variable in the config file
    logger.info("we exclude servers listed explictly in the config file")
    excluded_from_config = read_config_file("SHUTOFF_ALL_NON_WAZUH_SERVER_EXCLUDE")
    logger.info(
        "excluding %s servers listed in the config file", len(excluded_from_config)
    )
    selected_list, _, _ = compare_2_lists(selected_list, excluded_from_config)

    action_succeeded = True
    shutted_off_servers = []
    shutted_off_servers_failed = []
    for server_id in selected_list:
        output = _shutoff_server(conn, server_id, admin_lock)
        if output:
            shutted_off_servers.append(server_id)
        else:
            shutted_off_servers_failed.append(server_id)
            action_succeeded = False

    logger.info(
        "list of servers that have been set SHUTOFF:\n\n%s",
        "\n".join(shutted_off_servers),
    )
    logger.info(
        "list of servers that failed to SHUTOFF:\n\n%s",
        "\n".join(shutted_off_servers_failed),
    )

    logger.info("process to SHUTOFF Wazuh non-compliant servers performed")
    return action_succeeded
