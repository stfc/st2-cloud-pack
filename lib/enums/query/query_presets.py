from enum import Enum, auto


class QueryPresets(Enum):
    pass


class QueryPresetsGeneric(QueryPresets):
    """
    Enum class which holds generic query comparison operators
    """

    EQUAL_TO = auto()
    NOT_EQUAL_TO = auto()


class QueryPresetsInteger(QueryPresets):
    """
    Enum class which holds integer/float comparison operators
    """

    GREATER_THAN = auto()
    GREATER_THAN_OR_EQUAL_TO = auto()
    LESS_THAN = auto()
    LESS_THAN_OR_EQUAL_TO = auto()


class QueryPresetsDateTime(QueryPresets):
    """
    Enum class which holds datetime comparison operators
    """

    OLDER_THAN = auto()
    OLDER_THAN_OR_EQUAL_TO = auto()
    YOUNGER_THAN = auto()
    YOUNGER_THAN_OR_EQUAL_TO = auto()


class QueryPresetsString(QueryPresets):
    """
    Enum class which holds string comparison operators
    """

    ANY_IN = auto()
    MATCHES_REGEX = auto()
    NOT_ANY_IN = auto()
