class EOLServersWorkflow:
    """Identify and manage servers running an EOL operating system."""

    def __init__(self, conn, wazuh_client, elog_client, os_name, os_version):
        """
        Store the dependencies and input values used throughout the workflow.

        :param conn: OpenStack connection object
        :type conn: Connection
        :param wazuh_client: client used to query Wazuh
        :type wazuh_client: WazuhClient
        :param elog_client: client used to create records in ELOG
        :type elog_client: ElogClient
        :param os_name: operating-system name, for example ``ubuntu``
        :type os_name: str
        :param os_version: operating-system version, for example ``20``
        :type os_version: str
        """
        self.conn = conn
        self.wazuh_client = wazuh_client
        self.elog_client = elog_client
        self.os_name = os_name
        self.os_version = os_version

        # Values relating to the server currently being processed.
        self.server_id = None
        self.metadata = None
        self.metadata_age = None

    def find_eol_servers(self):
        """Return the IDs of servers running the configured EOL OS."""
        logger.info(
            "querying Wazuh to find servers running OS %s : %s",
            self.os_name,
            self.os_version,
        )

        server_list = self.wazuh_client.get_servers_for_os(
            self.os_name,
            self.os_version,
        )

        logger.info(
            "Wazuh queried for servers running OS %s : %s",
            self.os_name,
            self.os_version,
        )
        logger.info("returning %s Server IDs", len(server_list))

        return server_list

    def manage_new_eol_server(self):
        """Manage the current server when it has not previously been marked."""
        logger.info("starting the process to manage server %s", self.server_id)
        logger.info(
            "the server %s was never marked as running an EOL version of the OS",
            self.server_id,
        )
        logger.info(
            "marking the server %s as running an EOL version of the OS now",
            self.server_id,
        )

        set_metadata_foo_fixme()  # FIXME: pass/use self.server_id as required.

        logger.info(
            "server %s marked as running an EOL version of the OS",
            self.server_id,
        )

        username, email = find_user_info(
            self.server_id,
            self.conn._cloud_name,
        )

        if not email:
            logger.error(
                "there is no available information regarding the owner of Server %s",
                self.server_id,
            )
        else:
            logger.info(
                "notifying the owner of server %s about it running an EOL version of the OS",
                self.server_id,
            )

            email  # FIXME: send the notification using username/email.

            logger.info(
                "owner of server %s notified about it running an EOL version of the OS",
                self.server_id,
            )

        logger.info("process to manage server %s finished", self.server_id)

    def manage_old_eol_server(self):
        """Manage the current server when it has already been marked."""
        logger.info("starting the process to manage server %s", self.server_id)
        logger.info(
            "the server %s was already marked as running an EOL version of the OS",
            self.server_id,
        )

        self.metadata_age = ...  # FIXME: calculate the age of self.metadata.

        if self.metadata_age < minimum_age:  # FIXME: define/configure minimum_age.
            logger.info(
                "the user of server %s was notified %s ago, nothing to do yet",
                self.server_id,
                self.metadata_age,
            )
        else:
            shutoff_server(self.server_id)  # FIXME: use self.conn if required.
            notify_user()  # FIXME: notify the owner of self.server_id.
            elog()  # FIXME: create an ELOG record using self.elog_client.

        logger.info("process to manage server %s finished", self.server_id)

    def manage_eol_server(self):
        """Manage the server currently stored in ``self.server_id``."""
        logger.info(
            "starting the process to manage server %s running an EOL version of the OS",
            self.server_id,
        )

        self.metadata = get_metadata_foo_fixme()  # FIXME: use self.server_id.

        if not self.metadata:
            self.manage_new_eol_server()
        else:
            self.manage_old_eol_server()

        logger.info(
            "finished the process to manage server %s running an EOL version of the OS",
            self.server_id,
        )

    def eol_servers_workflow(self):
        """Identify and manage all servers running the configured EOL OS."""
        logger.info(
            "starting workflow to identify and manage EOL Servers for %s : %s",
            self.os_name,
            self.os_version,
        )

        server_list = self.find_eol_servers()

        for server_id in server_list:
            # Store shared per-server state on the instance so it does not need
            # to be passed through each method call.
            self.server_id = server_id
            self.metadata = None
            self.metadata_age = None
            self.manage_eol_server()

        # Avoid leaving the last processed server as active instance state.
        self.server_id = None
        self.metadata = None
        self.metadata_age = None

        logger.info(
            "finished workflow to identify and manage EOL Servers for %s : %s",
            self.os_name,
            self.os_version,
        )


def main(conn, wazuh_client, elog_client, os_name, os_version):
    x = EOLServersWorkflow(conn, wazuh_client, elog_client, os_name, os_version)
    x.eol_servers_workflow()

