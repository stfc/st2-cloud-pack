from typing import Type

from enums.query.props.aggregate_properties import AggregateProperties
from enums.query.props.prop_enum import PropEnum
from enums.query.query_presets import (
    QueryPresetsDateTime,
    QueryPresetsString,
    QueryPresetsGeneric,
)
from openstack_query.handlers.client_side_handler_datetime import (
    ClientSideHandlerDateTime,
)
from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from openstack_query.handlers.client_side_handler_string import ClientSideHandlerString
from openstack_query.handlers.server_side_handler import ServerSideHandler
from openstack_query.mappings.mapping_interface import MappingInterface
from openstack_query.runners.aggregate_runner import AggregateRunner
from openstack_query.runners.runner_wrapper import RunnerWrapper
from structs.query.query_client_side_handlers import QueryClientSideHandlers


class AggregateMapping(MappingInterface):
    """
    Mapping class for querying Openstack Aggregate objects
    Define property mappings, kwarg mappings and filter function mappings, and runner mapping related to hypervisors here
    """

    @staticmethod
    def get_chain_mappings():
        """
        Should return a dictionary containing property pairs mapped to query mappings.
        This is used to define how to chain results from this query to other possible queries
        """
        # TODO: find a way to map list of hostnames:
        #  AggregateProperties.HOST_IPS to HypervisorProperties.HYPERVISOR_NAME
        return None

    @staticmethod
    def get_runner_mapping() -> Type[RunnerWrapper]:
        """
        Returns a mapping to associated Runner class for the Query (AggregateRunner)
        """
        return AggregateRunner

    @staticmethod
    def get_prop_mapping() -> Type[AggregateProperties]:
        """
        Returns a mapping of valid presets for server side attributes (HypervisorProperties)
        """
        return AggregateProperties

    @staticmethod
    def get_server_side_handler() -> ServerSideHandler:
        """
        method to configure a server handler which can be used to get 'filter' keyword arguments that
        can be passed to openstack function conn.compute.aggregates() to filter results for a valid preset-property
        pair

        valid filters documented here:
            https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html
            https://docs.openstack.org/api-ref/compute/?expanded=list-hypervisors-detail#list-aggregates
        """
        # No server-side filters for AggregateQuery
        return ServerSideHandler({})

    @staticmethod
    def get_client_side_handlers() -> QueryClientSideHandlers:
        """
        method to configure a set of client-side handlers which can be used to get local filter functions
        corresponding to valid preset-property pairs. These filter functions can be used to filter results after
        listing all aggregates.
        """
        datetime_props = [
            AggregateProperties.AGGREGATE_DELETED_AT,
            AggregateProperties.AGGREGATE_UPDATED_AT,
            AggregateProperties.AGGREGATE_CREATED_AT,
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
            string_handler=ClientSideHandlerString(
                {
                    QueryPresetsString.MATCHES_REGEX: [
                        AggregateProperties.AGGREGATE_HOSTTYPE
                    ]
                }
            ),
            datetime_handler=ClientSideHandlerDateTime(
                {
                    QueryPresetsDateTime.OLDER_THAN: datetime_props,
                    QueryPresetsDateTime.YOUNGER_THAN: datetime_props,
                    QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO: datetime_props,
                    QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO: datetime_props,
                }
            ),
            integer_handler=None,
        )
