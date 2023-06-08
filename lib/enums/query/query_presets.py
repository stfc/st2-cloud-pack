from enum import Enum, auto


class QueryPresetsGeneric(Enum):
    # generic type comparison operators
    EQUAL_TO = auto()
    NOT_EQUAL_TO = auto()


class QueryPresetsInteger(Enum):
    # integer/float comparison operators
    GREATER_THAN = auto()
    LESS_THAN = auto()


class QueryPresetsDateTime(Enum):
    # datetime comparison operators
    OLDER_THAN = auto()
    YOUNGER_THAN = auto()
    YOUNGER_THAN_OR_EQUAL_TO = auto()
    OLDER_THAN_OR_EQUAL_TO = auto()


class QueryPresetsString(Enum):
    # string comparison operators
    ANY_IN = auto()
    NOT_ANY_IN = auto()
    MATCHES_REGEX = auto()
