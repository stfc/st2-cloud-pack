from dataclasses import dataclass
from typing import List


@dataclass
class TicketDetails:
    # pylint: disable=invalid-name
    dataTitle: dict
    dataBody: dict


@dataclass
class TicketInfo:
    # pylint: disable=invalid-name
    title: str
    body: str
    serverList: List[TicketDetails]
