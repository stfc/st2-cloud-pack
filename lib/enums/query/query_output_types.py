from enum import Enum, auto
from exceptions.parse_query_error import ParseQueryError


# pylint: disable=too-few-public-methods
class QueryOutputTypes(Enum):
    """
    Enum class which holds a list of supported query output options
    """

    TO_HTML = auto()
    TO_OBJECT_LIST = auto()
    TO_LIST = auto()
    TO_STR = auto()

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return QueryOutputTypes[val.upper()]
        except KeyError as err:
            raise ParseQueryError(
                f"Could not find return type flag {val}. "
                f"Available flags are {','.join([prop.name for prop in QueryOutputTypes])}"
            ) from err
