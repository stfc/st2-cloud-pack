from typing import Optional, Dict, Any, List

from openstack_query.handlers.client_side_handler import ClientSideHandler
from openstack_query.handlers.prop_handler import PropHandler
from openstack_query.handlers.server_side_handler import ServerSideHandler

from enums.query.query_presets import QueryPresets
from enums.query.props.prop_enum import PropEnum

from exceptions.parse_query_error import ParseQueryError
from exceptions.query_preset_mapping_error import QueryPresetMappingError
from exceptions.query_property_mapping_error import QueryPropertyMappingError

from custom_types.openstack_query.aliases import ClientSideFilterFunc, ServerSideFilters


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

        self._client_side_filter = None
        self._server_side_filters = None

    @property
    def client_side_filter(self) -> Optional[ClientSideFilterFunc]:
        return self._client_side_filter

    @property
    def server_side_filters(self) -> Optional[ServerSideFilters]:
        return self._server_side_filters

    def parse_where(
        self,
        preset: QueryPresets,
        prop: PropEnum,
        preset_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        method which parses and builds a filter function and (if possible) a set of openstack filter kwargs that
        corresponds to a given preset, property and set of preset arguments
        :param preset: Name of query preset to use
        :param prop: Name of property that the query preset will act on
        :param preset_kwargs: A set of arguments to pass to configure filter function and filter kwargs
        """

        if self._client_side_filter:
            raise ParseQueryError("Error: Already set a query preset")

        prop_func = self._prop_handler.get_prop_mapping(prop)
        if not prop_func:
            # If you are here from a search, you have likely forgotten to add it to the
            # client mapping variable in your Query object
            raise QueryPropertyMappingError(
                f"""
                Error: failed to get property mapping, given property
                {prop.name} is not supported in prop_handler
                """
            )

        preset_handler = self._get_preset_handler(preset, prop)
        self._client_side_filter = preset_handler.get_filter_func(
            preset, prop, prop_func, preset_kwargs
        )
        self._server_side_filters = self._server_side_handler.get_filters(
            preset, prop, prop_func, preset_kwargs
        )

    def _get_preset_handler(
        self, preset: QueryPresets, prop: PropEnum
    ) -> ClientSideHandler:
        """
        method which returns a preset handler object which supports the corresponding preset and property pair
        :param preset: A given preset that describes the query type
        :param prop: A prop which the preset will act on
        """

        # Most likely we have forgotten to add a mapping for a preset at the client-side
        # All presets should have a client-side handler associated to it
        if not any(i.preset_known(preset) for i in self._client_side_handlers):
            raise QueryPresetMappingError(
                "A preset with no known client side handler was passed. Please raise an issue with the repo maintainer"
            )

        for i in self._client_side_handlers:
            if i.check_supported(preset, prop):
                return i

        raise QueryPresetMappingError(
            f"Error: failed to get preset mapping, the preset '{preset.name}' cannot be "
            f"used on the property '{prop.name}' given.\n"
            f"If you believe it should, please raise an issue with repo maintainer"
        )
