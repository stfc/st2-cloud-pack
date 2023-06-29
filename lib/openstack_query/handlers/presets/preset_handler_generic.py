from typing import Any
from custom_types.openstack_query.aliases import PresetToValidPropsMap

from enums.query.query_presets import QueryPresets, QueryPresetsGeneric
from openstack_query.handlers.presets.preset_handler_base import PresetHandlerBase


class PresetHandlerGeneric(PresetHandlerBase):
    """
    Preset handler for Generic Presets.
    This class stores a dictionary which maps a Generic type preset to a filter function called FILTER_FUNCTIONS,
    and a dictionary which maps a Generic type preset to a list of supported properties called FILTER_FUNCTION_MAPPINGS.

    This class supports a set of methods to check and return a filter function for a given Generic type preset and
    property pair

    Filter functions which map to Generic type presets are defined here
    """

    def __init__(self, filter_function_mappings: PresetToValidPropsMap):
        super().__init__(filter_function_mappings)

        self._FILTER_FUNCTIONS = {
            QueryPresetsGeneric.EQUAL_TO: self._prop_equal_to,
            QueryPresetsGeneric.NOT_EQUAL_TO: self._prop_not_equal_to,
        }

    def _prop_not_equal_to(self, prop: Any, value: Any) -> bool:
        """
        Filter function which returns true if a prop is not equal to a given value
        :param prop: prop value to check against
        :param value: given value to check against
        """
        return not self._prop_equal_to(prop, value)

    @staticmethod
    def _prop_equal_to(prop: Any, value: Any) -> bool:
        """
        Filter function which returns true if a prop is equal to a given value
        :param prop: prop value to check against
        :param value: given value to check against
        """
        if isinstance(prop, type(value)):
            if isinstance(prop, object) and hasattr(prop, "__eq__"):
                return prop.__eq__(value)
        else:
            return False
        return prop == value
