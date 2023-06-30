from typing import Optional, Dict, Any, List
from enum import Enum

from openstack_query.handlers.client_side_handler import ClientSideHandler
from openstack_query.handlers.prop_handler import PropHandler
from openstack_query.handlers.server_side_handler import ServerSideHandler

from enums.query.query_presets import QueryPresets

from exceptions.parse_query_error import ParseQueryError
from exceptions.query_preset_mapping_error import QueryPresetMappingError
from exceptions.query_property_mapping_error import QueryPropertyMappingError


class QueryBuilder:
    """
    Helper class to handle setting and validating query parameters - primarily parsing 'where()' arguments to get
    filter function or kwarg params to use when running query
    """

    def __init__(
        self,
        prop_handler: PropHandler,
        client_side_handlers: List[ClientSideHandler],
        server_side_handler: Optional[ServerSideHandler],
    ):
        self._client_side_handlers = client_side_handlers
        self._prop_handler = prop_handler
        self._server_side_handler = server_side_handler

        self._filter_func = None
        self._server_side_filters = None

    @property
    def filter_func(self):
        return self._filter_func

    @property
    def server_side_filters(self):
        return self._server_side_filters

    def parse_where(
        self,
        preset: QueryPresets,
        prop: Enum,
        preset_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        method which parses and builds a filter function and (if possible) a set of openstack filter kwargs that
        corresponds to a given preset, property and set of preset arguments
        :param preset: Name of query preset to use
        :param prop: Name of property that the query preset will act on
        :param preset_kwargs: A set of arguments to pass to configure filter function and filter kwargs
        """

        if self._filter_func:
            raise ParseQueryError("Error: Already set a query preset")

        prop_func = self._prop_handler.get_prop_mapping(prop)
        if not prop_func:
            raise QueryPropertyMappingError(
                f"""
                Error: failed to get property mapping, given property
                {prop.name} is not supported in prop_handler
                """
            )

        preset_handler = self._get_preset_handler(preset, prop)
        self._filter_func = preset_handler.get_filter_func(
            preset, prop, prop_func, preset_kwargs
        )
        self._server_side_filters = self._server_side_handler.get_filters(
            preset, prop, prop_func, preset_kwargs
        )

    def _get_preset_handler(
        self, preset: QueryPresets, prop: Enum
    ) -> ClientSideHandler:
        """
        method which returns a preset handler object which supports the corresponding preset and property pair
        :param preset: A given preset that describes the query type
        :param prop: A prop which the preset will act on
        """
        for i in self._client_side_handlers:
            if i.check_supported(preset, prop):
                return i

        raise QueryPresetMappingError(
            """
                Error: failed to get preset mapping, the property cannot be
                used with the preset given. If you believe it should, please raise an
                issue with repo maintainer
            """
        )