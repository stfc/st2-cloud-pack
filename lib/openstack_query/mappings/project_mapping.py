from typing import Type

from structs.query.query_client_side_handlers import QueryClientSideHandlers

from enums.query.props.project_properties import ProjectProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsString,
)
from enums.query.props.server_properties import ServerProperties

from openstack_query.handlers.server_side_handler import ServerSideHandler
from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from openstack_query.handlers.client_side_handler_string import ClientSideHandlerString

from openstack_query.mappings.mapping_interface import MappingInterface
from openstack_query.runners.project_runner import ProjectRunner


class ProjectMapping(MappingInterface):
    """
    Mapping class for querying Openstack Flavor objects
    Define property mappings, kwarg mappings and filter function mappings, and runner mapping related to flavors here
    """

    @staticmethod
    def get_chain_mappings():
        """
        Should return a dictionary containing property pairs mapped to query mappings.
        This is used to define how to chain results from this query to other possible queries
        """
        return {ProjectProperties.PROJECT_ID: ServerProperties.PROJECT_ID}

    @staticmethod
    def get_runner_mapping() -> Type[ProjectRunner]:
        """
        Returns a mapping to associated Runner class for the Query (ProjectRunner)
        """
        return ProjectRunner

    @staticmethod
    def get_prop_mapping() -> Type[ProjectProperties]:
        """
        Returns a mapping of valid presets for server side attributes (ProjectProperties)
        """
        return ProjectProperties

    @staticmethod
    def get_server_side_handler() -> ServerSideHandler:
        """
        method to configure a server handler which can be used to get 'filter' keyword arguments that
        can be passed to openstack function conn.compute.flavors() to filter results for a valid preset-property pair

        valid filters documented here:
            https://docs.openstack.org/openstacksdk/latest/user/proxies/identity_v3.html
            https://docs.openstack.org/api-ref/identity/v3/index.html#list-projects
        """
        return ServerSideHandler(
            {
                QueryPresetsGeneric.EQUAL_TO: {
                    ProjectProperties.PROJECT_ID: lambda value: {"id": value},
                    ProjectProperties.PROJECT_DOMAIN_ID: lambda value: {
                        "domain_id": value
                    },
                    ProjectProperties.PROJECT_IS_ENABLED: lambda value: {
                        "is_enabled": value
                    },
                    ProjectProperties.PROJECT_IS_DOMAIN: lambda value: {
                        "is_domain": value
                    },
                    ProjectProperties.PROJECT_NAME: lambda value: {"name": value},
                    ProjectProperties.PROJECT_PARENT_ID: lambda value: {
                        "parent_id": value
                    },
                },
                QueryPresetsGeneric.NOT_EQUAL_TO: {
                    ProjectProperties.PROJECT_IS_ENABLED: lambda value: {
                        "is_enabled": not value
                    },
                    ProjectProperties.PROJECT_IS_DOMAIN: lambda value: {
                        "is_domain": not value
                    },
                },
                QueryPresetsGeneric.ANY_IN: {
                    ProjectProperties.PROJECT_ID: lambda values: [
                        {"id": value} for value in values
                    ],
                    ProjectProperties.PROJECT_DOMAIN_ID: lambda values: [
                        {"domain_id": value} for value in values
                    ],
                    ProjectProperties.PROJECT_NAME: lambda values: [
                        {"name": value} for value in values
                    ],
                    ProjectProperties.PROJECT_PARENT_ID: lambda values: [
                        {"parent_id": value} for value in values
                    ],
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
                        ProjectProperties.PROJECT_NAME,
                        ProjectProperties.PROJECT_DESCRIPTION,
                    ]
                }
            ),
            # set datetime query preset mappings
            datetime_handler=None,
            # set integer query preset mappings
            integer_handler=None,
        )
