from typing import Type

from enums.query.props.hypervisor_properties import HypervisorProperties
from structs.query.query_client_side_handlers import QueryClientSideHandlers

from enums.query.props.server_properties import ServerProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsDateTime,
    QueryPresetsString,
)
from enums.query.props.user_properties import UserProperties
from enums.query.props.project_properties import ProjectProperties
from enums.query.props.flavor_properties import FlavorProperties

from openstack_query.handlers.server_side_handler import ServerSideHandler

from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from openstack_query.handlers.client_side_handler_string import ClientSideHandlerString
from openstack_query.handlers.client_side_handler_datetime import (
    ClientSideHandlerDateTime,
)

from openstack_query.mappings.mapping_interface import MappingInterface
from openstack_query.runners.server_runner import ServerRunner

from openstack_query.time_utils import TimeUtils


class ServerMapping(MappingInterface):
    """
    Mapping class for querying Openstack Server objects.
    Define property mappings, kwarg mappings and filter function mappings, and runner mapping related to servers here
    """

    @staticmethod
    def get_chain_mappings():
        """
        Should return a dictionary containing property pairs mapped to query mappings.
        This is used to define how to chain results from this query to other possible queries
        """
        return {
            ServerProperties.USER_ID: UserProperties.USER_ID,
            ServerProperties.PROJECT_ID: ProjectProperties.PROJECT_ID,
            ServerProperties.FLAVOR_ID: FlavorProperties.FLAVOR_ID,
            ServerProperties.HYPERVISOR_ID: HypervisorProperties.HYPERVISOR_ID,
        }

    @staticmethod
    def get_runner_mapping() -> Type[ServerRunner]:
        """
        Returns a mapping to associated Runner class for the Query (ServerRunner)
        """
        return ServerRunner

    @staticmethod
    def get_prop_mapping() -> Type[ServerProperties]:
        """
        Returns a mapping of valid presets for server side attributes (ServerProperties)
        """
        return ServerProperties

    @staticmethod
    def get_server_side_handler() -> ServerSideHandler:
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
                    ServerProperties.SERVER_STATUS: lambda value: {"status": value},
                    ServerProperties.SERVER_CREATION_DATE: lambda value: {
                        "created_at": value
                    },
                    ServerProperties.FLAVOR_ID: lambda value: {"flavor": value},
                    ServerProperties.IMAGE_ID: lambda value: {"image": value},
                    ServerProperties.PROJECT_ID: lambda value: {"project_id": value},
                },
                QueryPresetsGeneric.ANY_IN: {
                    ServerProperties.USER_ID: lambda values: [
                        {"user_id": value} for value in values
                    ],
                    ServerProperties.SERVER_ID: lambda values: [
                        {"uuid": value} for value in values
                    ],
                    ServerProperties.SERVER_NAME: lambda values: [
                        {"hostname": value} for value in values
                    ],
                    ServerProperties.SERVER_DESCRIPTION: lambda values: [
                        {"description": value} for value in values
                    ],
                    ServerProperties.SERVER_STATUS: lambda values: [
                        {"status": value} for value in values
                    ],
                    ServerProperties.SERVER_CREATION_DATE: lambda values: [
                        {"created_at": value} for value in values
                    ],
                    ServerProperties.FLAVOR_ID: lambda values: [
                        {"flavor": value} for value in values
                    ],
                    ServerProperties.IMAGE_ID: lambda values: [
                        {"image": value} for value in values
                    ],
                    ServerProperties.PROJECT_ID: lambda values: [
                        {"project_id": value} for value in values
                    ],
                },
                QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: {
                    ServerProperties.SERVER_LAST_UPDATED_DATE: lambda func=TimeUtils.convert_to_timestamp, **kwargs: {
                        "changes-before": func(**kwargs)
                    }
                },
                QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: {
                    ServerProperties.SERVER_LAST_UPDATED_DATE: lambda func=TimeUtils.convert_to_timestamp, **kwargs: {
                        "changes-since": func(**kwargs)
                    }
                },
            }
        )

    @staticmethod
    def get_client_side_handlers() -> QueryClientSideHandlers:
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
                    QueryPresetsGeneric.ANY_IN: ["*"],
                    QueryPresetsGeneric.NOT_ANY_IN: ["*"],
                }
            ),
            # set string query preset mappings
            string_handler=ClientSideHandlerString(
                {
                    QueryPresetsString.MATCHES_REGEX: [
                        ServerProperties.SERVER_NAME,
                        ServerProperties.ADDRESSES,
                    ]
                }
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
