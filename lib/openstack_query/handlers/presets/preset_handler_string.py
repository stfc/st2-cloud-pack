import re

from typing import List, Any, Pattern
from custom_types.openstack_query.aliases import PresetToValidPropsMap

from enums.query.query_presets import QueryPresetsString
from openstack_query.handlers.presets.preset_handler_base import PresetHandlerBase
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError


class PresetHandlerString(PresetHandlerBase):
    """
    Preset handler for String Presets.
    This class stores a dictionary which maps a String type preset to a filter function called FILTER_FUNCTIONS,
    and a dictionary which maps a String type preset to a list of supported properties called FILTER_FUNCTION_MAPPINGS.

    This class supports a set of methods to check and return a filter function for a given String type preset and
    property pair

    Filter functions which map to String type presets are defined here
    """

    def __init__(self, filter_function_mappings: PresetToValidPropsMap):
        super().__init__(filter_function_mappings)

        self._FILTER_FUNCTIONS = {
            QueryPresetsString.ANY_IN: self._prop_any_in,
            QueryPresetsString.MATCHES_REGEX: self._prop_matches_regex,
            QueryPresetsString.NOT_ANY_IN: self._prop_not_any_in,
        }

    @staticmethod
    def _prop_matches_regex(prop: Any, regex_string: Pattern[str]) -> bool:
        """
        Filter function which returns true if a prop matches a regex pattern
        :param prop: prop value to check against
        :param regex_string: a regex pattern to run
        """
        return bool(re.match(regex_string, prop))

    @staticmethod
    def _prop_any_in(prop: Any, values: List[str]) -> bool:
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

    def _prop_not_any_in(self, prop: Any, values: List[str]) -> bool:
        """
        Filter function which returns true if a prop does not match any in a given list
        :param prop: prop value to check against
        :param values: a list of values to check against
        """
        return not self._prop_any_in(prop, values)
