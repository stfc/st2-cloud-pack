import logging
from typing import Optional, List
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

logger = logging.getLogger(__name__)


class ServerSideHandler(HandlerBase):
    """
    This class handles server side filtering.
    This class stores a dictionary which maps preset/property pairs to a set of filters that can be used
    when calling openstacksdk commands when listing openstack resources
    """

    def __init__(self, server_side_mappings: ServerSideFilterMappings):
        self._server_side_filter_mappings = server_side_mappings

    def get_supported_props(self, preset: QueryPresets) -> List[PropEnum]:
        """
        Gets a list of all supported properties for a given preset
        """
        return list(self._server_side_filter_mappings[preset].keys())

    def check_supported(self, preset: QueryPresets, prop: PropEnum) -> bool:
        """
        Method that returns True if a set of kwargs exist for a preset-property pair
        :param preset: A QueryPreset Enum for which a set of kwargs may exist for
        :param prop: A property Enum for which a set of kwargs may exist for
        """
        if not self.preset_known(preset):
            return False
        return prop in self._server_side_filter_mappings[preset].keys()

    def preset_known(self, preset: QueryPresets) -> bool:
        """
        Method that returns True if a preset is known to the handler
        :param preset: A QueryPreset Enum which may have filter function mappings known to the handler
        """
        return preset in self._server_side_filter_mappings.keys()

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
        return self._server_side_filter_mappings[preset][prop]

    def get_filters(
        self,
        preset: QueryPresets,
        prop: PropEnum,
        params: FilterParams,
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

        logger.debug(
            "found server-side filter function for preset %s: prop %s pair",
            preset.name,
            prop.name,
        )

        try:
            filters = filter_func(**params)
        except (KeyError, TypeError) as err:
            raise QueryPresetMappingError(
                "Preset Argument Error: failed to build server-side openstacksdk filters for preset:prop: "
                f"'{preset.name}':'{prop.name}' "
            ) from err

        if not isinstance(filters, list):
            return [filters]
        return filters
