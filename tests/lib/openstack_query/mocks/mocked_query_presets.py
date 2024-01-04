from typing import Dict
from enums.query.enum_with_aliases import EnumWithAliases

# pylint:disable=too-few-public-methods


class MockQueryPresets(EnumWithAliases):
    """
    An Enum class to mock query presets for various unit tests
    """

    @staticmethod
    def _get_aliases() -> Dict:
        # No mock aliases
        return {}

    ITEM_1 = 1
    ITEM_2 = 2
    ITEM_3 = 3
    ITEM_4 = 4
