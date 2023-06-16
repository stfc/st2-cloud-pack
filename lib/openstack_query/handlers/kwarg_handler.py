from enum import Enum
from typing import Dict, Optional
from enums.query.query_presets import QueryPresets

from custom_types.openstack_query.aliases import (
    PresetKwargs,
    KwargMappings,
    OpenstackFKwargFunc,
    OpenstackFilterKwargs,
)

from openstack_query.handlers.handler_base import HandlerBase
from exceptions.query_preset_mapping_error import QueryPresetMappingError


class KwargHandler(HandlerBase):
    def __init__(self, kwarg_mappings: KwargMappings):
        self._KWARG_MAPPINGS = kwarg_mappings

    def check_supported(self, preset: QueryPresets, prop: Enum) -> bool:
        props_valid_for_preset = self._KWARG_MAPPINGS.get(preset, None)
        if props_valid_for_preset:
            if prop in props_valid_for_preset.keys():
                return True
        return False

    def _get_mapping(
        self, preset: QueryPresets, prop: Enum
    ) -> Optional[OpenstackFKwargFunc]:
        if not self.check_supported(preset, prop):
            return None
        return self._KWARG_MAPPINGS[preset][prop]

    def get_kwargs(
        self,
        preset: QueryPresets,
        prop: Enum,
        kwarg_params: Optional[PresetKwargs] = None,
    ) -> Optional[OpenstackFilterKwargs]:
        kwarg_func = self._get_mapping(preset, prop)
        if not kwarg_func:
            return None
        try:
            _ = self._check_kwarg_mapping(kwarg_func, kwarg_params)
        except TypeError as err:
            raise QueryPresetMappingError(
                "Preset Argument Error: failed to build openstack filter kwargs for preset:prop"
                f"'{preset.name}', '{prop.name}'"
            ) from err
        return kwarg_func(**kwarg_params)

    @staticmethod
    def _check_kwarg_mapping(
        kwarg_func: OpenstackFKwargFunc, kwarg_params: PresetKwargs
    ) -> bool:
        try:
            _ = kwarg_func(**kwarg_params)
        except KeyError as e:
            raise TypeError(f"expected arg '{e.args[0]}' but not found")
        return True
