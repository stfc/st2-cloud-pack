from typing import Dict, Optional

from structs.query.query_client_side_handlers import QueryClientSideHandlers

from enums.query.server_properties import ServerProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsDateTime,
    QueryPresetsString,
    QueryPresetsInteger,
)
from openstack_query.handlers.server_side_handler import ServerSideHandler
from openstack_query.handlers.prop_handler import PropHandler


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


class QueryServer(QueryWrapper):
    """
    Query class for querying Openstack Server objects.
    Define property mappings, kwarg mappings and filter function mappings related to servers here
    """

    def _get_prop_handler(self) -> PropHandler:
        """
        method to configure a property handler which can be used to get any valid property of a openstack Server object
        valid properties are documented here:
        https://docs.openstack.org/openstacksdk/latest/user/resources/compute/v2/server.html#openstack.compute.v2.server.Server

        """
        return PropHandler(
            {
                ServerProperties.USER_ID: lambda a: a["user_id"],
                ServerProperties.HYPERVISOR_ID: lambda a: a["host_id"],
                ServerProperties.SERVER_ID: lambda a: a["id"],
                ServerProperties.SERVER_NAME: lambda a: a["name"],
                ServerProperties.SERVER_DESCRIPTION: lambda a: a["description"],
                ServerProperties.SERVER_STATUS: lambda a: a["status"],
                ServerProperties.SERVER_CREATION_DATE: lambda a: a["created_at"],
                ServerProperties.SERVER_LAST_UPDATED_DATE: lambda a: a["updated_at"],
                ServerProperties.FLAVOR_ID: lambda a: ["flavor_id"],
                ServerProperties.IMAGE_ID: lambda a: ["image_id"],
                ServerProperties.PROJECT_ID: lambda a: a["location"]["project"]["id"],
            }
        )

    def _get_server_side_handler(self) -> ServerSideHandler:
        """
        method to configure a server handler which can be used to get 'filter' keyword arguments that
        can be passed to openstack function conn.compute.servers() to filter results for a valid preset-property pair

        valid filters documented here:
            https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html
            https://docs.openstack.org/api-ref/compute/?expanded=list-servers-detail#list-server-request
        """
        return ServerSideHandler(
            {
                QueryPresetsGeneric.EQUAL_TO: {
                    ServerProperties.USER_ID: lambda value: {"user_id": value},
                    ServerProperties.SERVER_ID: lambda value: {"uuid": value},
                    ServerProperties.SERVER_NAME: lambda value: {"hostname": value},
                    ServerProperties.SERVER_DESCRIPTION: lambda value: {
                        "description": value
                    },
                    ServerProperties.SERVER_STATUS: lambda value: {"vm_state": value},
                    ServerProperties.SERVER_CREATION_DATE: lambda value: {
                        "created_at": value
                    },
                    ServerProperties.FLAVOR_ID: lambda value: {"flavor": value},
                    ServerProperties.IMAGE_ID: lambda value: {"image": value},
                    ServerProperties.PROJECT_ID: lambda value: {"project_id": value},
                },
                QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: {
                    ServerProperties.SERVER_LAST_UPDATED_DATE: lambda **kwargs: {
                        "changes-before": TimeUtils.convert_to_timestamp(**kwargs)
                    }
                },
                QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: {
                    ServerProperties.SERVER_LAST_UPDATED_DATE: lambda **kwargs: {
                        "changes-since": TimeUtils.convert_to_timestamp(**kwargs)
                    }
                },
            }
        )

    def _get_client_side_handlers(self) -> QueryClientSideHandlers:
        """
        method to configure a set of client-side handlers which can be used to get local filter functions
        corresponding to valid preset-property pairs. These filter functions can be used to filter results after
        listing all servers.
        """
        return QueryClientSideHandlers(
            # set generic query preset mappings
            generic_handler=ClientSideHandlerGeneric(
                {
                    QueryPresetsGeneric.EQUAL_TO: ["*"],
                    QueryPresetsGeneric.NOT_EQUAL_TO: ["*"],
                }
            ),
            # set string query preset mappings
            string_handler=ClientSideHandlerString(
                {QueryPresetsString.MATCHES_REGEX: [ServerProperties.SERVER_NAME]}
            ),
            # set datetime query preset mappings
            datetime_handler=ClientSideHandlerDateTime(
                {
                    QueryPresetsDateTime.OLDER_THAN: [
                        ServerProperties.SERVER_CREATION_DATE,
                        ServerProperties.SERVER_LAST_UPDATED_DATE,
                    ],
                    QueryPresetsDateTime.YOUNGER_THAN: [
                        ServerProperties.SERVER_CREATION_DATE,
                        ServerProperties.SERVER_LAST_UPDATED_DATE,
                    ],
                    QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: [
                        ServerProperties.SERVER_CREATION_DATE,
                        ServerProperties.SERVER_LAST_UPDATED_DATE,
                    ],
                    QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: [
                        ServerProperties.SERVER_CREATION_DATE,
                        ServerProperties.SERVER_LAST_UPDATED_DATE,
                    ],
                }
            ),
            # set integer query preset mappings
            integer_handler=None,
        )

    def __init__(self):
        super().__init__(runner=ServerRunner())
