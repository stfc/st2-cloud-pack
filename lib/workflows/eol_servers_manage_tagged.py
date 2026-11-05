import logging
from typing import List
from openstack.connection import Connection
from apis.wazuh_api.structs.wazuh_account import WazuhAccount
from apis.wazuh_api.wazuh_query_agents import wazuh_list_servers_by_os

from apis.utils.time_utils import days_since_timestamp
from apis.utils.diff_utils import compare_2_lists

from apis.openstack_api.openstack_server import (
    find_servers_with_tag,
    shutoff_server,
    admin_lock_server,
    remove_tag_from_server,
    delete_metadata_from_server,
    get_server_owner_email,
    get_server_status,
    get_server_name,
    get_project_name,
    get_metadata_from_server,
)
from apis.openstack_api.enums.server_status import ServerStatus
from apis.utils.read_config import read_config_file

logger = logging.getLogger(__name__)


class FixedTaggedServer:
    def __init__(self, conn, config, server_id):
        self.conn = conn
        self.servers_eol_tag = config["SERVERS_EOL_TAG"]
        self.servers_eol_metadata_key_os = config["SERVERS_EOL_METADATA_KEY_OS"]
        self.servers_eol_metadata_key_timestamp = config[
            "SERVERS_EOL_METADATA_KEY_TIMESTAMP"
        ]
        self.server_id = server_id

    def unmark_server(self) -> None:
        """
        the Server is now fine
        we remove the tags and the metadata
        """
        logger.info(
            "removing tag %s from server %s", self.servers_eol_tag, self.server_id
        )
        remove_tag_from_server(self.conn, self.server_id, self.servers_eol_tag)
        logger.info("removing metadata from server %s", self.server_id)
        delete_metadata_from_server(
            self.conn, self.server_id, [self.servers_eol_metadata_key_os]
        )
        delete_metadata_from_server(
            self.conn, self.server_id, [self.servers_eol_metadata_key_timestamp]
        )

    def process(self):
        self.unmark_server()


class NotFixedTaggedServer:
    def __init__(self, conn, config, server_id):
        self.conn = conn
        self.servers_eol_metadata_key_timestamp = config[
            "SERVERS_EOL_METADATA_KEY_TIMESTAMP"
        ]
        self.servers_eol_days_grace_period = config["SERVERS_EOL_DAYS_GRACE_PERIOD"]
        self.server_id = server_id

    @property
    def email(self):
        return get_server_owner_email(self.conn, self.server_id)

    @property
    def server_name(self):
        return get_server_name(self.conn, self.server_id)

    @property
    def project_name(self):
        return get_project_name(self.conn, self.server_id)

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

    def shutdown_server(self) -> None:
        """
        the Server is still running an unsupported OS,
        still Active, and the User was notified long ago

        we set the Server SHUTOFF with admin lock
        """
        logger.info("shutting off server %s", self.server_id)
        shutoff_server(self.conn, self.server_id)

    def lock_server(self) -> None:
        logger.info("admin lock for server %s", self.server_id)
        reason = (
            "Server still running unsupported version of the Operating System "
            f"more than {self.servers_eol_days_grace_period} days "
            "after User was notified"
        )
        admin_lock_server(self.conn, self.server_id, reason)

    def process(self):
        if self.server_is_active and self.grace_period_passed:
            self.shutdown_server()
            self.lock_server()


# pylint: disable=too-few-public-methods
class FixedTaggedServerList:
    def __init__(self, conn, config, server_id_list):
        self.server_list = [
            FixedTaggedServer(conn, config, server_id) for server_id in server_id_list
        ]

    def process(self):
        for server in self.server_list:
            server.process()


class NotFixedTaggedServerList:
    def __init__(self, conn, config, server_id_list, **email_params):
        self.email_params = email_params
        self.server_list = [
            NotFixedTaggedServer(conn, config, server_id)
            for server_id in server_id_list
        ]
        self.user_d = {}

    def process(self):
        for server in self.server_list:
            server.process()

    def notify(self):
        for server in self.server_list:
            email = server.email
            if email not in self.user_d:
                self.user_d[email] = TaggedServerCollection(email, **self.email_params)
            self.user_d[email].add(server)

        for coll in self.user_d.values():
            coll.send_email()


class TaggedServerCollection:
    def __init__(self, email_address, **email_params):
        self.email_address = email_address
        self.server_list = []

    def add(self, server):
        self.server_list.append(server)

    def send_email(self):
        # TO BE IMPLEMENTED
        pass


def _query_wazuh(wazuh_account: WazuhAccount, config) -> List:
    """
    query Wazuh for the entire list of Servers running
    on any of the unsupported versions of the Operating System
    as listed in the configuration file
    """
    server_list = []
    servers_eol_operating_systems = config["SERVERS_EOL_OPERATING_SYSTEMS"]
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


# ==============================================================================
#   main
# ==============================================================================


def eol_servers_manage_tagged(conn, wazuh_account, **email_params):

    config = read_config_file()

    wazuh_server_list = _query_wazuh(wazuh_account, config)
    servers_eol_tag = config["SERVERS_EOL_TAG"]
    tagged_server_list = find_servers_with_tag(conn, servers_eol_tag)
    _, fixed, not_fixed = compare_2_lists(wazuh_server_list, tagged_server_list)

    fixed_list = FixedTaggedServerList(conn, config, fixed)
    fixed_list.process()
    not_fixed_list = NotFixedTaggedServerList(conn, config, not_fixed, **email_params)
    not_fixed_list.process()
    not_fixed_list.notify()
