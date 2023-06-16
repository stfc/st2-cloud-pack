from typing import Any
from custom_types.openstack_query.aliases import PresetToValidPropsMap

from enums.query.query_presets import QueryPresets, QueryPresetsGeneric
from openstack_query.handlers.presets.preset_handler_base import PresetHandlerBase


class PresetHandlerGeneric(PresetHandlerBase):
    def __init__(self, filter_function_mappings: PresetToValidPropsMap):
        super().__init__(filter_function_mappings)

        self._FILTER_FUNCTIONS = {
            QueryPresetsGeneric.EQUAL_TO: self._prop_equal_to,
            QueryPresetsGeneric.NOT_EQUAL_TO: self._prop_not_equal_to,
        }

    def _prop_not_equal_to(self, prop: Any, value: Any) -> bool:
        return not self._prop_equal_to(prop, value)

    @staticmethod
    def _prop_equal_to(prop: Any, value: Any) -> bool:
        if isinstance(prop, type(value)):
            if isinstance(prop, object) and hasattr(prop, "__eq__"):
                return prop.__eq__(value)
        else:
            return False
        return prop == value
