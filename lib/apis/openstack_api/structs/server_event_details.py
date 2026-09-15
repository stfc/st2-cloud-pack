from datetime import datetime
from typing import NamedTuple

from apis.openstack_api.enums.server_event import ServerEvent


class ServerEventDetails(NamedTuple):
    """
    A single event from a Server's event list
    with the date the event occurred
    """

    event: ServerEvent
    date: datetime
