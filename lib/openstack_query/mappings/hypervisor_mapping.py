from typing import Type

from enums.query.props.hypervisor_properties import HypervisorProperties
from enums.query.props.server_properties import ServerProperties
from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsString,
    QueryPresetsInteger,
)
from openstack_query.handlers.client_side_handler_generic import (
    ClientSideHandlerGeneric,
)
from openstack_query.handlers.client_side_handler_integer import (
    ClientSideHandlerInteger,
)
from openstack_query.handlers.client_side_handler_string import ClientSideHandlerString
from openstack_query.handlers.server_side_handler import ServerSideHandler
from openstack_query.mappings.mapping_interface import MappingInterface

from openstack_query.runners.hypervisor_runner import HypervisorRunner
from openstack_query.runners.runner_wrapper import RunnerWrapper
from structs.query.query_client_side_handlers import QueryClientSideHandlers


class HypervisorMapping(MappingInterface):
    """
    Mapping class for querying Openstack Hypervisor objects
    Define property mappings, kwarg mappings and filter function mappings, and runner mapping related to hypervisors here
    """

    @staticmethod
    def get_chain_mappings():
        """
        Should return a dictionary containing property pairs mapped to query mappings.
        This is used to define how to chain results from this query to other possible queries
        """
        return {HypervisorProperties.HYPERVISOR_ID: ServerProperties.HYPERVISOR_ID}

    @staticmethod
    def get_runner_mapping() -> Type[RunnerWrapper]:
        """
        Returns a mapping to associated Runner class for the Query (HypervisorRunner)
        """
        return HypervisorRunner

    @staticmethod
    def get_prop_mapping() -> Type[HypervisorProperties]:
        """
        Returns a mapping of valid presets for server side attributes (HypervisorProperties)
        """
        return HypervisorProperties

    @staticmethod
    def get_server_side_handler() -> ServerSideHandler:
        """
        method to configure a server handler which can be used to get 'filter' keyword arguments that
        can be passed to openstack function conn.compute.hypervisors() to filter results for a valid preset-property
        pair

        valid filters documented here:
            https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html
            https://docs.openstack.org/api-ref/compute/?expanded=list-hypervisors-detail
        """
        # No server-side filters for HypervisorQuery
        return ServerSideHandler({})

    @staticmethod
    def get_client_side_handlers() -> QueryClientSideHandlers:
        """
        method to configure a set of client-side handlers which can be used to get local filter functions
        corresponding to valid preset-property pairs. These filter functions can be used to filter results after
        listing all hypervisors.
        """
        integer_props = [
            HypervisorProperties.HYPERVISOR_DISK_USED,
            HypervisorProperties.HYPERVISOR_DISK_FREE,
            HypervisorProperties.HYPERVISOR_DISK_SIZE,
            HypervisorProperties.HYPERVISOR_MEMORY_SIZE,
            HypervisorProperties.HYPERVISOR_MEMORY_USED,
            HypervisorProperties.HYPERVISOR_MEMORY_FREE,
            HypervisorProperties.HYPERVISOR_VCPUS,
            HypervisorProperties.HYPERVISOR_VCPUS_USED,
            HypervisorProperties.HYPERVISOR_SERVER_COUNT,
            HypervisorProperties.HYPERVISOR_CURRENT_WORKLOAD,
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
                {
                    QueryPresetsString.MATCHES_REGEX: [
                        HypervisorProperties.HYPERVISOR_IP,
                        HypervisorProperties.HYPERVISOR_NAME,
                        HypervisorProperties.HYPERVISOR_DISABLED_REASON,
                    ]
                }
            ),
            # set datetime query preset mappings
            datetime_handler=None,
            # set integer query preset mappings
            integer_handler=ClientSideHandlerInteger(
                {
                    QueryPresetsInteger.LESS_THAN: integer_props,
                    QueryPresetsInteger.GREATER_THAN: integer_props,
                    QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO: integer_props,
                    QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO: integer_props,
                }
            ),
        )
