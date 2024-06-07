import re

from typing import Union
from custom_types.openstack_query.aliases import PresetPropMappings

from enums.query.query_presets import QueryPresetsString
from openstack_query.handlers.client_side_handler import ClientSideHandler

# pylint: disable=too-few-public-methods


class ClientSideHandlerString(ClientSideHandler):
    """
    Client Side handler for String related queries.
    This class stores a dictionary which maps a String preset/prop pairs to a filter function
    Filter functions which map to QueryPresetsString are defined here
    """

    def __init__(self, preset_prop_mappings: PresetPropMappings):
        filter_mappings = {
            QueryPresetsString.MATCHES_REGEX: self._prop_matches_regex,
        }
        super().__init__(filter_mappings, preset_prop_mappings)

    @staticmethod
    def _prop_matches_regex(prop: Union[str, None], value: str) -> bool:
        """
        Filter function which returns true if a prop matches a regex pattern
        :param prop: prop value to check against
        :param value: a string which can be converted into a valid regex pattern to run
        """
        if prop is None:
            return False
        res = re.match(re.compile(rf"{value}"), prop)
        return bool(res)
