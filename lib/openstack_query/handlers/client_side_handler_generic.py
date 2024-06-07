from typing import Any, List
from custom_types.openstack_query.aliases import PresetPropMappings, PropValue

from enums.query.query_presets import QueryPresetsGeneric
from openstack_query.handlers.client_side_handler import ClientSideHandler
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError

# pylint: disable=too-few-public-methods


class ClientSideHandlerGeneric(ClientSideHandler):
    """
    Client Side handler for 'Generic' queries.
    This class stores a dictionary which maps a Generic preset/prop pairs to a filter function
    Filter functions which map to QueryPresetsGeneric are defined here
    """

    def __init__(self, preset_prop_mappings: PresetPropMappings):
        filter_mappings = {
            QueryPresetsGeneric.ANY_IN: self._prop_any_in,
            QueryPresetsGeneric.EQUAL_TO: self._prop_equal_to,
            QueryPresetsGeneric.NOT_ANY_IN: self._prop_not_any_in,
            QueryPresetsGeneric.NOT_EQUAL_TO: self._prop_not_equal_to,
        }
        super().__init__(filter_mappings, preset_prop_mappings)

    @staticmethod
    def _prop_not_any_in(prop: Any, values: List[PropValue]) -> bool:
        """
        Filter function which returns true if a prop does not match any in a given list
        :param prop: prop value to check against
        :param values: a list of values to check against
        """
        if len(values) == 0:
            raise MissingMandatoryParamError(
                "values list must contain at least one item to match against"
            )
        res = any(prop == val for val in values)
        return not res

    @staticmethod
    def _prop_any_in(prop: Any, values: List[PropValue]) -> bool:
        """
        Filter function which returns true if a prop matches any in a given list
        :param prop: prop value to check against
        :param values: a list of values to check against
        """
        if len(values) == 0:
            raise MissingMandatoryParamError(
                "values list must contain at least one item to match against"
            )
        return any(prop == val for val in values)

    @staticmethod
    def _prop_not_equal_to(prop: Any, value: PropValue) -> bool:
        """
        Filter function which returns true if a prop is not equal to a given value
        :param prop: prop value to check against
        :param value: given value to check against
        """
        return not prop == value

    @staticmethod
    def _prop_equal_to(prop: Any, value: PropValue) -> bool:
        """
        Filter function which returns true if a prop is equal to a given value
        :param prop: prop value to check against
        :param value: given value to check against
        """
        return prop == value
