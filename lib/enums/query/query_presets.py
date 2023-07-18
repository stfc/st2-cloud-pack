from enum import Enum, auto
from exceptions.parse_query_error import ParseQueryError


class QueryPresets(Enum):
    pass


class QueryPresetsGeneric(QueryPresets):
    """
    Enum class which holds generic query comparison operators
    """

    EQUAL_TO = auto()
    NOT_EQUAL_TO = auto()

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return QueryPresetsGeneric[val.upper()]
        except KeyError as err:
            raise ParseQueryError(
                f"Could not find preset type {val}. "
                f"Available preset types are {','.join([prop.name for prop in QueryPresetsGeneric])}"
            ) from err


class QueryPresetsInteger(QueryPresets):
    """
    Enum class which holds integer/float comparison operators
    """

    GREATER_THAN = auto()
    GREATER_THAN_OR_EQUAL_TO = auto()
    LESS_THAN = auto()
    LESS_THAN_OR_EQUAL_TO = auto()

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return QueryPresetsInteger[val.upper()]
        except KeyError as err:
            raise ParseQueryError(
                f"Could not find preset type {val}. "
                f"Available preset types are {','.join([prop.name for prop in QueryPresetsInteger])}"
            ) from err


class QueryPresetsDateTime(QueryPresets):
    """
    Enum class which holds datetime comparison operators
    """

    OLDER_THAN = auto()
    OLDER_THAN_OR_EQUAL_TO = auto()
    YOUNGER_THAN = auto()
    YOUNGER_THAN_OR_EQUAL_TO = auto()

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return QueryPresetsDateTime[val.upper()]
        except KeyError as err:
            raise ParseQueryError(
                f"Could not find preset type {val}. "
                f"Available preset types are {','.join([prop.name for prop in QueryPresetsDateTime])}"
            ) from err


class QueryPresetsString(QueryPresets):
    """
    Enum class which holds string comparison operators
    """

    ANY_IN = auto()
    MATCHES_REGEX = auto()
    NOT_ANY_IN = auto()

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return QueryPresetsString[val.upper()]
        except KeyError as err:
            raise ParseQueryError(
                f"Could not find preset type {val}. "
                f"Available preset types are {','.join([prop.name for prop in QueryPresetsString])}"
            ) from err
