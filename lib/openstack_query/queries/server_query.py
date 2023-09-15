from typing import Type

from structs.query.query_client_side_handlers import QueryClientSideHandlers

from enums.query.props.server_properties import ServerProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsDateTime,
    QueryPresetsString,
)
from openstack_query.handlers.server_side_handler import ServerSideHandler


from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from openstack_query.handlers.client_side_handler_string import ClientSideHandlerString
from openstack_query.handlers.client_side_handler_datetime import (
    ClientSideHandlerDateTime,
)

from openstack_query.queries.query_wrapper import QueryWrapper
from openstack_query.runners.server_runner import ServerRunner

from openstack_query.time_utils import TimeUtils


class ServerQuery(QueryWrapper):
    """
    Query class for querying Openstack Server objects.
    Define property mappings, kwarg mappings and filter function mappings related to servers here
    """
