from typing import Optional, Tuple
from enums.query.query_presets import QueryPresets
from enums.query.props.prop_enum import PropEnum

from custom_types.openstack_query.aliases import (
    FilterParams,
    ServerSideFilterMappings,
    ServerSideFilterFunc,
    ServerSideFilters,
)

from openstack_query.handlers.handler_base import HandlerBase
from exceptions.query_preset_mapping_error import QueryPresetMappingError


class ServerSideHandler(HandlerBase):
    """
    This class handles server side filtering.
    This class stores a dictionary which maps preset/property pairs to a set of filters that can be used
    when calling openstacksdk commands when listing openstack resources
    """

    def __init__(self, kwarg_mappings: ServerSideFilterMappings):
        self._SERVER_SIDE_FILTER_MAPPINGS = kwarg_mappings

    def check_supported(self, preset: QueryPresets, prop: PropEnum) -> bool:
        """
        Method that returns True if a set of kwargs exist for a preset-property pair
        :param preset: A QueryPreset Enum for which a set of kwargs may exist for
        :param prop: A property Enum for which a set of kwargs may exist for
        """
        if not self.preset_known(preset):
            return False
        return prop in self._SERVER_SIDE_FILTER_MAPPINGS[preset].keys()

    def preset_known(self, preset: QueryPresets) -> bool:
        """
        Method that returns True if a preset is known to the handler
        :param preset: A QueryPreset Enum which may have filter function mappings known to the handler
        """
        return preset in self._SERVER_SIDE_FILTER_MAPPINGS.keys()

    def _get_mapping(
        self, preset: QueryPresets, prop: PropEnum
    ) -> Optional[ServerSideFilterFunc]:
        """
        Method that returns a function which takes a set of args and returns a dictionary of filter kwargs to pass to an
        openstack list function (returns None if no kwarg mapping exists)
        :param preset: A QueryPreset Enum for which a kwarg mapping may exist for
        :param prop: A property Enum for which a kwarg mapping may exist for
        """
        if not self.check_supported(preset, prop):
            return None
        return self._SERVER_SIDE_FILTER_MAPPINGS[preset][prop]

    def get_filters(
        self,
        preset: QueryPresets,
        prop: PropEnum,
        params: Optional[FilterParams] = None,
    ) -> Optional[ServerSideFilters]:
        """
        Method that returns a dictionary of server side filter params to pass to an openstack list function
        :param preset: A QueryPreset Enum for which a filter mapping may exist for
        :param prop: A property Enum for which a filter mapping may exist for
        :param params: A set of optional parameters to pass to configure filters
        """
        filter_func = self._get_mapping(preset, prop)
        if not filter_func:
            return None
        res, reason = self._check_filter_mapping(filter_func, params)
        if not res:
            raise QueryPresetMappingError(
                "Preset Argument Error: failed to build server-side openstacksdk filters for preset:prop: "
                f"'{preset.name}':'{prop.name}' "
                f"reason: {reason}"
            )
        return filter_func(**params)

    @staticmethod
    def _check_filter_mapping(
        filter_func: ServerSideFilterFunc, filter_params: FilterParams
    ) -> Tuple[bool, str]:
        """
        Method that checks if optional parameters are valid for the kwarg mapping function
        :param filter_func: lambda filter func to check
        :param filter_params: a dictionary of params to check if valid for filter func
        """
        try:
            filter_func(**filter_params)
        except TypeError as err:
            return False, f"expected arg '{err.args[0]}' but not found"
        return True, ""
