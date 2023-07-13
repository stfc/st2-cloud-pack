from typing import Union
from custom_types.openstack_query.aliases import PresetPropMappings

from enums.query.query_presets import QueryPresetsInteger
from openstack_query.handlers.client_side_handler import ClientSideHandler

# pylint: disable=too-few-public-methods


class ClientSideHandlerInteger(ClientSideHandler):
    """
    Client Side handler for Integer related queries.
    This class stores a dictionary which maps an Integer preset/prop pairs to a filter function
    Filter functions which map to QueryPresetsInteger are defined here
    """

    def __init__(self, _filter_function_mappings: PresetPropMappings):
        super().__init__(_filter_function_mappings)

        self._filter_functions = {
            QueryPresetsInteger.GREATER_THAN: self._prop_greater_than,
            QueryPresetsInteger.LESS_THAN: self._prop_less_than,
            QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO: self._prop_greater_than_or_equal_to,
            QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO: self._prop_less_than_or_equal_to,
        }

    @staticmethod
    def _prop_less_than(prop: Union[int, float], value: Union[int, float]) -> bool:
        """
        Filter function which returns true if a prop is less than a given value
        :param prop: prop value to check against
        :param value: given value to check against
        """
        return prop < value

    @staticmethod
    def _prop_greater_than(prop: Union[int, float], value: Union[int, float]) -> bool:
        """
        Filter function which returns true if a prop is greater than a given value
        :param prop: prop value to check against
        :param value: given value to check against
        """
        return prop > value

    @staticmethod
    def _prop_less_than_or_equal_to(
        prop: Union[int, float], value: Union[int, float]
    ) -> bool:
        """
        Filter function which returns true if a prop is less than or equal to a given value
        :param prop: prop value to check against
        :param value: given value to check against
        """
        return prop <= value

    @staticmethod
    def _prop_greater_than_or_equal_to(
        prop: Union[int, float], value: Union[int, float]
    ) -> bool:
        """
        Filter function which returns true if a prop is greater than or equal to a given value
        :param prop: prop value to check against
        :param value: given value to check against
        """
        return prop >= value
