from enum import Enum


class SortOrder(Enum):
    """
    Enum class which holds enums for sort order. Used to specify sort order when
    querying and parsing query using sort_by
    """

    ASC = False
    DESC = True
