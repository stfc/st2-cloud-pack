import logging
from typing import List
from openstack.connection import Connection
from apis.wazuh_api.structs.wazuh_account import WazuhAccount
from apis.elog_api.structs.elog_account import ElogAccount
from apis.wazuh_api.wazuh_query_agents import wazuh_list_servers_by_os
from apis.openstack_api.openstack_server import (
    find_servers_with_tag,
    shutofff_server,
    add_tag_to_server,
    remove_tag_from_server,
    add_metadata_to_server,
    delete_metadata_from_server,
    get_server_owner_email,
)
from apis.openstack_query_api.user_queries import find_user_info
from apis.elog_api.elog import add_record_to_elog
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------


def _timestamp() -> str:
    """
    return a timestamp for the current time in UTC
    """
    n = datetime.now(timezone.utc)
    return n.strftime("%Y-%m-%d %H:%M:%S (UTC)")


# ------------------------------------------------------------------------------


def _compare_lists(wazuh_l: List[str], tagged_l: List[str]):
    """
    compares 2 lists (A and B) and returns 3:
    * one with items only in list A
    * one with items only in list B
    * one with items in both lists A and B
    """
    wazuh_s = set(wazuh_l)
    tagged_s = set(tagged_l)
    only_wazuh = list(wazuh_s - tagged_s)
    only_tagged = list(tagged_s - wazuh_s)
    both = list(wazuh_s.intersection(tagged_s))
    return only_wazuh, only_tagged, both


# ------------------------------------------------------------------------------


def manage_new_eol_server(conn: Connection, server_id: str) -> None:
    add_tag_to_server(conn, server_id, "tag_fixme")
    add_metadata_to_server(conn, server_id, properties_fixme)
    try:
        email = get_server_owner_email(conn, server_id)
        send_email()  # FIXME
    except Exception as ex:
        logger.error(
            "there is no avaible information regarding the owner of Server %s",
            server_id,
        )


def manage_new_eol_server_list(conn: Connection, only_wazuh_list: List[str]) -> None:
    for server_id in only_wazuh_list:
        manage_new_eol_server(conn, server_id)


# ------------------------------------------------------------------------------


def manage_old_eol_server(
    conn: Connection, elog_account: ElogAccount, server_id: str
) -> None:
    metadata = get_metadata_foo_fixme()
    metadata_age = get_metadata_age_foo_fixme()
    if metadata_age < minimum_age:
        logger.info(
            "the user of server %s was notified %s ago, nothing to do yet",
            server_id,
            metadata_age,
        )
    else:
        shutoff_server(conn, server_id)
        send_email()  # FIXME
        add_record_to_elog(elog_account, "subject_fixme", "body_fixme")


def manage_old_eol_server_list(
    conn: Connection, elog_account: ElogAccount, server_l: List[str]
) -> None:
    for server in server_l:
        manage_old_eol_server(conn, elog_account, server)


# ------------------------------------------------------------------------------


def manage_fixed_server(
    conn: Connection, elog_account: ElogAccount, server_id: str
) -> None:
    delete_metadata_from_server(conn, server_id, properties_fixme)
    remove_tag_from_server(conn, server_id, "tag_fixme")
    add_record_to_elog(elog_account, "subject_fixme", "body_fixme")


def manage_fixed_server_list(
    conn: Connection, elog_account: ElogAccount, server_l: List[str]
) -> None:
    for server in server_l:
        manage_fixed_server(conn, elog_account, server)


# ------------------------------------------------------------------------------
#
# main function
#
# ------------------------------------------------------------------------------


def eol_servers_workflow(
    conn: Connection,
    wazuh_account: WazuhAccount,
    elog_account: ElogAccount,
    os_name: str,
    os_version: str,
) -> None:

    wazuh_server_list = wazuh_list_servers_by_os(wazuh_account, os_name, os_version)
    tagged_server_list = find_servers_with_tag(conn, "tag_fixme")
    only_wazuh_list, only_tagged_list, both_list = _compare_lists(
        wazuh_server_list, tagged_server_list
    )
    manage_new_eol_server_list(conn, only_wazuh_list)
    manage_old_eol_server_list(conn, elog_account, both_list)
    manage_fixed_server_list(conn, elog_account, only_tagged_list)
