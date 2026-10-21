import logging
from typing import List
from openstack.connection import Connection
from apis.wazuh_api.structs.wazuh_account import WazuhAccount
from apis.wazuh_api.wazuh_query_agents import wazuh_list_servers_by_os

from apis.utils.time_utils import days_since_timestamp

from apis.openstack_api.openstack_server import (
    find_servers_with_tag,
    shutoff_server,
    admin_lock_server,
    remove_tag_from_server,
    delete_metadata_from_server,
    get_server_status,
    get_metadata_from_server,
)
from apis.openstack_api.enums.server_status import ServerStatus
from apis.utils.read_config import read_config_file

logger = logging.getLogger(__name__)


class TaggedServer:
    def __init__(self, conn: Connection, server_id: str):
        self.conn = conn
        self.server_id = server_id
        self.server_eol_tag = read_config_file("SERVERS_EOL_TAG")
        self.servers_eol_metadata_key_os = read_config_file(
            "SERVERS_EOL_METADATA_KEY_OS"
        )
        self.servers_eol_metadata_key_timestamp = read_config_file(
            "SERVERS_EOL_METADATA_KEY_TIMESTAMP"
        )
        self.servers_eol_days_grace_period = read_config_file(
            "SERVERS_EOL_DAYS_GRACE_PERIOD"
        )

    def unmark_server(self) -> None:
        """
        the Server is now fine
        we remove the tags and the metadata
        """
        logger.info(
            "removing tag %s from server %s", self.server_eol_tag, self.server_id
        )
        remove_tag_from_server(self.conn, self.server_id, self.server_eol_tag)
        logger.info("removing EOL markers from server %s metadata", self.server_id)
        delete_metadata_from_server(
            self.conn,
            self.server_id,
            [self.servers_eol_metadata_key_os, self.servers_eol_metadata_key_timestamp],
        )

    def shutdown_and_lock_server(self) -> None:
        """
        the Server is still running an unsupported OS,
        still Active, and the User was notified long ago

        we set the Server SHUTOFF with admin lock
        """
        logger.info("shutting off server %s", self.server_id)
        shutoff_server(self.conn, self.server_id)
        logger.info("admin lock for server %s", self.server_id)
        reason = (
            "Server still running unsupported version of the Operating System "
            f"more than {self.servers_eol_days_grace_period} days after User was notified"
        )
        admin_lock_server(self.conn, self.server_id, reason)

    @property
    def server_is_active(self) -> bool:
        """
        return True is this Server is Active
        """
        return get_server_status(self.conn, self.server_id) == ServerStatus.ACTIVE

    @property
    def grace_period_passed(self) -> bool:
        """
        check if the Server was marked at least 7 days ago
        """
        metadata_timestamp = get_metadata_from_server(
            self.conn, self.server_id, self.servers_eol_metadata_key_timestamp
        )
        days = days_since_timestamp(metadata_timestamp)
        logger.info("server %s was marked % days ago", self.server_id, days)
        return days > self.servers_eol_days_grace_period

    def process_eol_server(self, wazuh_server_list: List) -> None:
        """
        process this Server
        * if the Server is no longer in Wazuh,
          meaning it was fixed by the User,
          we remove the tag and all metadata
        * if the Server is still in Wazuh, is Active,
          and the user was notified long ago,
          we SHUTOFF it and lock it so it cannot be re-activated
        """
        logger.info("processing server %s", self.server_id)
        if self.server_id not in wazuh_server_list:
            self.unmark_server()
        else:
            if self.server_is_active and self.grace_period_passed:
                self.shutdown_and_lock_server()
        logger.info("server %s processed successfully", self.server_id)


def query_wazuh(wazuh_account: WazuhAccount) -> List:
    """
    query Wazuh for the entire list of Servers running
    on any of the unsupported versions of the Operating System
    as listed in the configuration file
    """
    server_list = []
    servers_eol_operating_systems = read_config_file("SERVERS_EOL_OPERATING_SYSTEMS")
    # operating_systems is a list of dictionaries, it looks like this
    #    [{'os': 'ubuntu', 'version': '20'},
    #     {'os': 'scientific', 'version': '7'}
    #    ]
    for os in servers_eol_operating_systems:
        os_name = os["os"]
        os_version = os["version"]
        server_list += wazuh_list_servers_by_os(wazuh_account, os_name, os_version)
    logger.info("found %s servers in Wazuh", len(server_list))
    return server_list


# ------------------------------------------------------------------------------
#   main
# ------------------------------------------------------------------------------


def hygiene_eol_manage_tagged_servers(conn, wazuh_account) -> None:
    wazuh_server_list = query_wazuh(wazuh_account)
    servers_eol_tag = read_config_file("SERVERS_EOL_TAG")
    tagged_server_list = find_servers_with_tag(conn, servers_eol_tag)
    for server_id in tagged_server_list:
        server = TaggedServer(conn, server_id)
        server.process_eol_server(wazuh_server_list)
