from enum import auto
from enums.query.props.prop_enum import PropEnum

# pylint: disable=too-few-public-methods


class ServerProperties(PropEnum):
    """
    An enum class for all server properties
    """

    FLAVOR_ID = auto()
    HYPERVISOR_ID = auto()
    IMAGE_ID = auto()
    PROJECT_ID = auto()
    SERVER_CREATION_DATE = auto()
    SERVER_DESCRIPTION = auto()
    SERVER_ID = auto()
    SERVER_LAST_UPDATED_DATE = auto()
    SERVER_NAME = auto()
    SERVER_STATUS = auto()
    USER_ID = auto()
