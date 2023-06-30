from typing import List, Callable, Any, Dict
from enum import Enum
from enums.query.query_presets import QueryPresets


PropFunc = Callable[[Any], Any]
PropToPropFuncMap = Dict[Enum, PropFunc]

PresetKwargs = Dict[str, Any]
FilterFunc = Callable[[PropFunc, PresetKwargs], bool]
PresetToFilterFuncMap = Dict[QueryPresets, FilterFunc]
PresetToValidPropsMap = Dict[QueryPresets, List[Enum]]


ParsedFilterFunc = Callable[[Any], bool]

ServerSideFilters = Dict[str, Any]
ServerSideFilterFunc = Callable[[Any], ServerSideFilters]

PropToServerSideFilterFunc = Dict[Enum, ServerSideFilterFunc]
ServerSideFilterMappings = Dict[QueryPresets, PropToServerSideFilterFunc]
