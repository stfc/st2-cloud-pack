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

    @property
    def prop_mapping(self) -> Type[ServerProperties]:
        return ServerProperties

    @property
    def query_runner(self) -> ServerRunner:
        return ServerRunner(self.prop_mapping)

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
