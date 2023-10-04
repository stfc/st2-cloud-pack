import re

from typing import Any
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

    def __init__(self, filter_function_mappings: PresetPropMappings):
        super().__init__(filter_function_mappings)

        self._filter_functions = {
            QueryPresetsString.MATCHES_REGEX: self._prop_matches_regex,
        }

    def _prop_matches_regex(self, prop: Any, regex_string: str) -> bool:
        """
        Filter function which returns true if a prop matches a regex pattern
        :param prop: prop value to check against
        :param regex_string: a string which can be converted into a valid regex pattern to run
        """
        return bool(re.match(re.compile(regex_string), prop))
