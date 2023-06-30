from enum import Enum
from typing import Optional, Tuple
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
    """
    This class stores a dictionary which maps a preset and property pair to a function which returns a dictionary which
    can be passed as kwargs to an openstack list resource function - and will act as a filter which
    corresponds to the preset. This dictionary is called KWARG_MAPPINGS
    """

    def __init__(self, kwarg_mappings: KwargMappings):
        self._KWARG_MAPPINGS = kwarg_mappings

    def check_supported(self, preset: QueryPresets, prop: Enum) -> bool:
        """
        Method that returns True if a set of kwargs exist for a preset-property pair
        :param preset: A QueryPreset Enum for which a set of kwargs may exist for
        :param prop: A property Enum for which a set of kwargs may exist for
        """
        props_valid_for_preset = self._KWARG_MAPPINGS.get(preset, None)
        if props_valid_for_preset:
            if prop in props_valid_for_preset.keys():
                return True
        return False

    def _get_mapping(
        self, preset: QueryPresets, prop: Enum
    ) -> Optional[OpenstackFKwargFunc]:
        """
        Method that returns a function which takes a set of args and returns a dictionary of kwargs to pass to an
        openstack list function (returns None if no kwarg mapping exists)
        :param preset: A QueryPreset Enum for which a kwarg mapping may exist for
        :param prop: A property Enum for which a kwarg mapping may exist for
        """
        if not self.check_supported(preset, prop):
            return None
        return self._KWARG_MAPPINGS[preset][prop]

    def get_kwargs(
        self,
        preset: QueryPresets,
        prop: Enum,
        kwarg_params: Optional[PresetKwargs] = None,
    ) -> Optional[OpenstackFilterKwargs]:
        """
        Method that returns a dictionary of kwargs to pass to an openstack list function
        :param preset: A QueryPreset Enum for which a kwarg mapping may exist for
        :param prop: A property Enum for which a kwarg mapping may exist for
        :param kwarg_params: A set of optional parameters to pass to kwarg mapping function
        """
        kwarg_func = self._get_mapping(preset, prop)
        if not kwarg_func:
            return None
        res, reason = self._check_kwarg_mapping(kwarg_func, kwarg_params)
        if not res:
            raise QueryPresetMappingError(
                "Preset Argument Error: failed to build openstack filter kwargs for preset:prop"
                f"'{preset.name}', '{prop.name}'"
                f"reason: {reason}"
            )
        return kwarg_func(**kwarg_params)

    @staticmethod
    def _check_kwarg_mapping(
        kwarg_func: OpenstackFKwargFunc, kwarg_params: PresetKwargs
    ) -> Tuple[bool, str]:
        """
        Method that checks if optional parameters are valid for the kwarg mapping function
        :param kwarg_func: kwarg lambda func to check
        :param kwarg_params: a dictionary of params to check if valid
        """
        try:
            kwarg_func(**kwarg_params)
        except KeyError as err:
            return False, f"expected arg '{err.args[0]}' but not found"
        return True, ""
