from typing import Dict, TypeVar, List, Type

from openstack_query.mappings.mapping_interface import MappingInterface
from openstack_query.mappings.server_mapping import ServerMapping

MappingType = TypeVar("MappingType", bound=Type[MappingInterface])

MAPPING_REGISTRY: List[MappingType] = [ServerMapping]
