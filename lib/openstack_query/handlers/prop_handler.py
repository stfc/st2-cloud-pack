from enum import Enum
from typing import Any, Optional, Set
from custom_types.openstack_query.aliases import PropToPropFuncMap, PropFunc
from openstack_query.handlers.handler_base import HandlerBase


class PropHandler:
    def __init__(self, property_mappings: PropToPropFuncMap):
        self._PROPERTY_MAPPINGS = property_mappings

    def check_supported(self, prop: Enum):
        return prop in self._PROPERTY_MAPPINGS.keys()

    def _get_mapping(self, prop: Enum) -> Optional[PropFunc]:
        return self._PROPERTY_MAPPINGS.get(prop, None)

    def all_props(self) -> Set[Enum]:
        return set(self._PROPERTY_MAPPINGS.keys())

    def get_prop(self, item: Any, prop: Enum, default_out: str = "Not Found") -> str:
        if not self.check_supported(prop):
            return default_out

        prop_func = self._get_mapping(prop)
        try:
            return str(prop_func(item))
        except AttributeError:
            return default_out
