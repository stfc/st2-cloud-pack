from enum import Enum, auto


class ServerProperties(Enum):
    USER_ID = auto()
    HYPERVISOR_ID = auto()
    SERVER_ID = auto()
    SERVER_NAME = auto()
    SERVER_DESCRIPTION = auto()
    SERVER_STATUS = auto()
    SERVER_CREATION_DATE = auto()
    SERVER_LAST_UPDATED_DATE = auto()
    FLAVOR_ID = auto()
    IMAGE_ID = auto()
    PROJECT_ID = auto()