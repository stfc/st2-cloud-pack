from enum import Enum, auto


# pylint: disable=too-few-public-methods
class QueryOutputTypes(Enum):
    """
    Holds the list of supported query output options
    """

    TO_HTML = auto()
    TO_OBJECT_LIST = auto()
    TO_LIST = auto()
    TO_STR = auto()
