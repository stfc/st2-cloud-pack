from typing import Union
from custom_types.openstack_query.aliases import PresetToValidPropsMap

from enums.query.query_presets import QueryPresets, QueryPresetsInteger
from openstack_query.handlers.presets.preset_handler_base import PresetHandlerBase


class PresetHandlerInteger(PresetHandlerBase):
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
        return prop < value

    @staticmethod
    def _prop_greater_than(prop: Union[int, float], value: Union[int, float]) -> bool:
        return prop > value

    @staticmethod
    def _prop_less_than_or_equal_to(
        prop: Union[int, float], value: Union[int, float]
    ) -> bool:
        return prop <= value

    @staticmethod
    def _prop_greater_than_or_equal_to(
        prop: Union[int, float], value: Union[int, float]
    ) -> bool:
        return prop >= value
