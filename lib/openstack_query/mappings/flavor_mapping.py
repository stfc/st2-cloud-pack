from typing import Type
from structs.query.query_client_side_handlers import QueryClientSideHandlers

from enums.query.props.flavor_properties import FlavorProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsInteger,
    QueryPresetsString,
)

from openstack_query.handlers.server_side_handler import ServerSideHandler
from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from openstack_query.handlers.client_side_handler_integer import (
    ClientSideHandlerInteger,
)
from openstack_query.handlers.client_side_handler_string import ClientSideHandlerString

from openstack_query.mappings.mapping_interface import MappingInterface
from openstack_query.runners.flavor_runner import FlavorRunner


class FlavorMapping(MappingInterface):
    """
    Mapping class for querying Openstack Flavor objects
    Define property mappings, kwarg mappings and filter function mappings, and runner mapping related to flavors here
    """

    @staticmethod
    def get_runner_mapping() -> Type[FlavorRunner]:
        """
        Returns a mapping to associated Runner class for the Query (FlavorRunner)
        """
        return FlavorRunner

    @staticmethod
    def get_prop_mapping() -> Type[FlavorProperties]:
        """
        Returns a mapping of valid presets for server side attributes (FlavorProperties)
        """
        return FlavorProperties

    @staticmethod
    def get_server_side_handler() -> ServerSideHandler:
        """
        method to configure a server handler which can be used to get 'filter' keyword arguments that
        can be passed to openstack function conn.compute.flavors() to filter results for a valid preset-property pair

        valid filters documented here:
            https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html
            https://docs.openstack.org/api-ref/compute/?expanded=list-servers-detail#show-flavor-details
        """
        return ServerSideHandler(
            {
                QueryPresetsGeneric.EQUAL_TO: {
                    FlavorProperties.FLAVOR_IS_PUBLIC: lambda value: {
                        "is_public": value
                    }
                },
                QueryPresetsGeneric.NOT_EQUAL_TO: {
                    FlavorProperties.FLAVOR_IS_PUBLIC: lambda value: {
                        "is_public": not value
                    }
                },
                QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO: {
                    FlavorProperties.FLAVOR_DISK: lambda value: {"minDisk": int(value)},
                    FlavorProperties.FLAVOR_RAM: lambda value: {"minRam": int(value)},
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

        integer_prop_list = [
            FlavorProperties.FLAVOR_RAM,
            FlavorProperties.FLAVOR_DISK,
            FlavorProperties.FLAVOR_EPHEMERAL,
            FlavorProperties.FLAVOR_SWAP,
            FlavorProperties.FLAVOR_VCPU,
        ]

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
                {QueryPresetsString.MATCHES_REGEX: [FlavorProperties.FLAVOR_NAME]}
            ),
            # set datetime query preset mappings
            datetime_handler=None,
            # set integer query preset mappings
            integer_handler=ClientSideHandlerInteger(
                {
                    QueryPresetsInteger.LESS_THAN: integer_prop_list,
                    QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO: integer_prop_list,
                    QueryPresetsInteger.GREATER_THAN: integer_prop_list,
                    QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO: integer_prop_list,
                }
            ),
        )
