from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Callable, Any, Optional, Type

from exceptions.parse_query_error import ParseQueryError

PropFunc = Callable[[Any], Any]


class PropEnum(Enum):
    """
    An enum base class for all openstack resource properties - for type annotation purposes
    """

    @staticmethod
    def _from_string_impl(val: str, prop_cls: Type[PropEnum]):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return prop_cls[val.upper()]
        except KeyError as err:
            raise ParseQueryError(
                f"Could not find property {val}. "
                f"Available properties are {','.join([prop.name for prop in prop_cls])}"
            ) from err

    @staticmethod
    @abstractmethod
    def get_prop_mapping(prop) -> Optional[PropFunc]:
        """
        Method that returns the property function if function mapping exists for a given property Enum
        :param prop: A property Enum for which a function may exist for
        """

    @staticmethod
    @abstractmethod
    def get_marker_prop_func():
        """
        A getter method to return marker property function for pagination
        """
