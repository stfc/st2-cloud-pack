from typing import Union
from custom_types.openstack_query.aliases import PresetToValidPropsMap

from enums.query.query_presets import QueryPresetsInteger
from openstack_query.handlers.presets.preset_handler_base import PresetHandlerBase


class PresetHandlerInteger(PresetHandlerBase):
    """
    Preset handler for Integer Presets.
    This class stores a dictionary which maps a Integer type preset to a filter function called FILTER_FUNCTIONS,
    and a dictionary which maps a Integer type preset to a list of supported properties called FILTER_FUNCTION_MAPPINGS.

    This class supports a set of methods to check and return a filter function for a given Integer type preset and
    property pair

    Filter functions which map to Integer type presets are defined here
    """

    def __init__(self, filter_function_mappings: PresetToValidPropsMap):
        super().__init__(filter_function_mappings)

        self._FILTER_FUNCTIONS = {
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
