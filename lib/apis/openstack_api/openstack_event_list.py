import logging
from typing import List

from apis.openstack_api.enums.server_event import ServerEvent
from apis.openstack_api.structs.server_event_details import ServerEventDetails
from apis.utils.time_utils import parse_iso_utc

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

        self._events = []

        server = conn.compute.get_server(server_id)
        action_list = conn.compute.server_actions(server)

        for unparsed_event in action_list:
            event_type = ServerEvent.from_string(unparsed_event.action)
            self._events.append(
                ServerEventDetails(
                    event=event_type,
                    date=parse_iso_utc(unparsed_event.start_time),
                )
            )

        # the output of server_actions() is a generator
        self.logger.debug(
            "Object EventList for Server ID %s initialised properly", server_id
        )

    @property
    def events(self):
        return self._events

    @events.setter
    def events(self, events: List[ServerEvent]):
        assert all(isinstance(event, ServerEventDetails) for event in events)
        self._events = events

    @property
    def last_event(self):
        """
        return: the last Event for this Server
        rtype: ServerAction
        """
        return sorted(self.events, key=lambda x: x.date, reverse=True)[0]
