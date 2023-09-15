import types
from typing import Type, TypeVar, List

from openstack_query.api.query_api import QueryAPI
from openstack_query.mappings import MappingInterface, MAPPING_REGISTRY
from openstack_query.queries.query_factory import QueryFactory
from structs.query.query_impl import QueryImpl

# Hide the fact that a mapping interface is being used
# which also decouples the mapping from the dynamic query
# type in the IDE inspection
QueryT = TypeVar("QueryT", bound=MappingInterface)


def export_query_types() -> list[type]:
    """
    Exports a list of callable methods dynamically, e.g. ServerQuery, UserQuery, etc.
    These will use the factory to inject their implementation on the fly, separating
    the implementation from the public API.
    """
    registered_mappings = []
    for mapping_cls in MAPPING_REGISTRY:

        def _inject_deps() -> QueryImpl:
            return QueryFactory.build_query_deps(mapping_cls)

        mapping_name = mapping_cls.__name__.replace("Mapping", "")
        new_type = type(
            f"{mapping_name}Query", (QueryAPI,), {"_inject_deps": _inject_deps}
        )
        registered_mappings.append(new_type)

    return registered_mappings
