import logging
from datetime import datetime, timezone
from openstack.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class EventList:
    """
    a class to handle information related to the "Event List"
    for a give Server.
    For example, to get for how long the Server has been in the
    current state.
    """

    def __init__(self, conn, server_id):
        """
        :param conn: the Openstack Connection
        :type conn: openstack.connection.Connection
        :param server_id: the ID of the Server
        :type server_id: str
        :raises Exception: exception raised when the Server ID is not valid
        """
        self.logger = logging.getLogger("EventList")
        # first we check the Server actually exists
        try:
            conn.compute.get_server(server_id)
            self.logger.debug("Verified the Server ID %s actually exists", server_id)
        except NotFoundException as ex:
            self.logger.error(
                "The Server ID %s does not exist. This EventList object cannot be initialised. Raising an Exception.",
                server_id,
            )
            raise ex
        self.events = list(conn.compute.server_actions(server_id))
        # the output of server_actions() is a generator
        self.logger.debug(
            "Object EventList for Server ID %s initialised properly", server_id
        )

    @property
    def last_event(self):
        """
        return: the last Event for this Server
        rtype: ServerAction
        """
        self.logger.debug("Getting the last event")
        # the last Event happens to be the first item in the EventList
        return self.events[0]

    @property
    def seconds_in_current_state(self):
        """
        :return: for how long the server has been in the current state
        :rtype: int
        """
        self.logger.debug("Getting the number seconds in current state")
        last_event_t = self.last_event.start_time
        # last_event_t looks like this
        # 2024-07-25T12:08:40.000000
        last_event_dt = datetime.fromisoformat(last_event_t).replace(
            tzinfo=timezone.utc
        )
        time_delta = datetime.now(timezone.utc) - last_event_dt
        seconds = int(time_delta.total_seconds())
        self.logger.info("Number seconds in current state is %s", seconds)
        return seconds
