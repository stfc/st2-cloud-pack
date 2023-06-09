import re

from typing import List, Any, Pattern


from enums.query.query_presets import QueryPresets, QueryPresetsString
from openstack_query.preset_handlers.preset_handler_base import PresetHandlerBase
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError


class PresetHandlerString(PresetHandlerBase):
    def __init__(self):
        self._FILTER_FUNCTIONS = {
            QueryPresetsString.ANY_IN: self._prop_any_in,
            QueryPresetsString.MATCHES_REGEX: self._prop_matches_regex,
            QueryPresetsString.NOT_ANY_IN: self._prop_not_any_in,
        }

    @staticmethod
    def _prop_matches_regex(prop: Any, regex_string: Pattern[str]) -> bool:
        return True if re.match(regex_string, prop) else False

    @staticmethod
    def _prop_any_in(prop: Any, values: List[str]) -> bool:
        if len(values) == 0:
            raise MissingMandatoryParamError(
                "values list must contain at least one item to match against"
            )
        return any(prop == val for val in values)

    def _prop_not_any_in(self, prop: Any, values: List[str]) -> bool:
        return not self._prop_any_in(prop, values)
