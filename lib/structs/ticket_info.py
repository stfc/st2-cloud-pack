from dataclasses import dataclass


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
    server_list: list
