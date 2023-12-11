from typing import Dict
from enums.query.enum_with_aliases import EnumWithAliases


class SortOrder(EnumWithAliases):
    """
    Enum class which holds enums for sort order. Used to specify sort order when
    querying and parsing query using sort_by
    """

    ASC = False
    DESC = True

    @staticmethod
    def _get_aliases() -> Dict:
        return {
            SortOrder.ASC: ["ascending"],
            SortOrder.DESC: ["descending"],
        }
