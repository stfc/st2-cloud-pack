from abc import abstractmethod
from enum import Enum
from typing import Dict

from exceptions.parse_query_error import ParseQueryError


class EnumWithAliases(Enum):
    """
    Enum class which stores aliases which can be mapped onto stored enums
    """

    @staticmethod
    @abstractmethod
    def _get_aliases() -> Dict:
        """
        A method that returns all valid string aliases for a given property enum
        """

    @classmethod
    def from_string(cls, val: str):
        """
        A class method that converts string alias to enum
        :param val: string value that is to be converted to an enum
        """
        for prop_enum in cls:
            valid_aliases = cls._get_aliases().get(prop_enum, [])

            # if val matches prop_enum.name, then directly return without looking at mappings
            if val.casefold() == prop_enum.name.casefold() or any(
                val.casefold() == i.casefold() for i in valid_aliases
            ):
                return prop_enum
        raise ParseQueryError(
            f"Could not parse string alias {val}. "
            f"The string alias not valid for any of the following Enums {','.join([prop.name for prop in cls])}"
        )
