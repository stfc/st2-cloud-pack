from enum import auto
from enums.query.enum_with_aliases import EnumWithAliases
from exceptions.parse_query_error import ParseQueryError

# pylint: disable=too-few-public-methods


class QueryPresets(EnumWithAliases):
    @staticmethod
    def _get_aliases():
        pass


class QueryPresetsGeneric(QueryPresets):
    """
    Enum class which holds generic query comparison operators
    """

    EQUAL_TO = auto()
    NOT_EQUAL_TO = auto()
    ANY_IN = auto()
    NOT_ANY_IN = auto()

    @staticmethod
    def _get_aliases():
        """
        A method that returns all valid string alias mappings
        """
        return {
            QueryPresetsGeneric.EQUAL_TO: ["equal", "=="],
            QueryPresetsGeneric.NOT_EQUAL_TO: ["not_equal", "!="],
            QueryPresetsGeneric.ANY_IN: ["in"],
            QueryPresetsGeneric.NOT_ANY_IN: ["not_in"],
        }


class QueryPresetsInteger(QueryPresets):
    """
    Enum class which holds integer/float comparison operators
    """

    GREATER_THAN = auto()
    GREATER_THAN_OR_EQUAL_TO = auto()
    LESS_THAN = auto()
    LESS_THAN_OR_EQUAL_TO = auto()

    @staticmethod
    def _get_aliases():
        """
        A method that returns all valid string alias mappings
        """
        return {}


class QueryPresetsDateTime(QueryPresets):
    """
    Enum class which holds datetime comparison operators
    """

    OLDER_THAN = auto()
    OLDER_THAN_OR_EQUAL_TO = auto()
    YOUNGER_THAN = auto()
    YOUNGER_THAN_OR_EQUAL_TO = auto()

    @staticmethod
    def _get_aliases():
        """
        A method that returns all valid string alias mappings
        """
        return {}


class QueryPresetsString(QueryPresets):
    """
    Enum class which holds string comparison operators
    """

    MATCHES_REGEX = auto()

    @staticmethod
    def _get_aliases():
        """
        A method that returns all valid string alias mappings
        """
        return {QueryPresetsString.MATCHES_REGEX: ["regex", "match_regex"]}


def get_preset_from_string(val: str):
    """
    function that takes a string and returns a preset Enum if that string is an alias for that preset
    :param val: a string alias to convert
    """
    for preset_cls in [
        QueryPresetsGeneric,
        QueryPresetsString,
        QueryPresetsDateTime,
        QueryPresetsInteger,
    ]:
        try:
            return preset_cls.from_string(val)
        except ParseQueryError:
            continue
    raise ParseQueryError(f"Could not find preset that matches alias {val}.")
