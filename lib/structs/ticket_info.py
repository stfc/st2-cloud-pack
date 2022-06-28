from dataclasses import dataclass


@dataclass
class TicketDetails:
    # pylint: disable=invalid-name
    dataTitle: dict
    dataBody: dict

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass
class TicketInfo:
    # pylint: disable=invalid-name
    title: str
    body: str
    server_list: list

    def __getitem__(self, item):
        return getattr(self, item)
