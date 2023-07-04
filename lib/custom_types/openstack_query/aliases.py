from typing import List, Callable, Any, Dict, Union, Literal
from enum import Enum
from enums.query.query_presets import QueryPresets

from openstack.identity.v3.project import Project

OpenstackResourceObj = Any

PropFunc = Callable[[OpenstackResourceObj], Dict[str, Any]]
PropertyMappings = Dict[Enum, PropFunc]

PresetKwargs = Dict[str, Any]

FilterFunc = Callable[[PropFunc, PresetKwargs], bool]
PresetToFilterFuncMap = Dict[QueryPresets, FilterFunc]
PresetToValidPropsMap = Dict[QueryPresets, List[Enum]]

ClientSideFilterFunc = Callable[[OpenstackResourceObj], bool]

ServerSideFilters = Dict[str, Any]
ServerSideFilterFunc = Callable[[Any], ServerSideFilters]

PropToServerSideFilterFunc = Dict[Enum, ServerSideFilterFunc]
ServerSideFilterMappings = Dict[QueryPresets, PropToServerSideFilterFunc]

ClientSidePropMapping = Union[List[Enum], List[Literal["*"]]]

ProjectIdentifier = Union[str, Project]
