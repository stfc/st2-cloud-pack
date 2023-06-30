from typing import Any
from custom_types.openstack_query.aliases import PresetToValidPropsMap

from enums.query.query_presets import QueryPresetsGeneric
from openstack_query.handlers.client_side_handler import ClientSideHandler


class ClientSideHandlerGeneric(ClientSideHandler):
    """
    Client Side handler for 'Generic' queries.
    This class stores a dictionary which maps a Generic preset/prop pairs to a filter function
    Filter functions which map to QueryPresetsGeneric are defined here
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

    def _prop_equal_to(self, prop: Any, value: Any) -> bool:
        """
        Filter function which returns true if a prop is equal to a given value
        :param prop: prop value to check against
        :param value: given value to check against
        """
        return prop == value
