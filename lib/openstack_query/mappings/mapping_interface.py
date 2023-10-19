from typing import Type
from abc import ABC, abstractmethod
from enums.query.props.prop_enum import PropEnum
from structs.query.query_client_side_handlers import QueryClientSideHandlers
from openstack_query.runners.runner_wrapper import RunnerWrapper
from openstack_query.handlers.server_side_handler import ServerSideHandler


class MappingInterface(ABC):
    """
    Abstract Base class. This class defines abstract getter methods to enforce Query classes implement
    server-side, client-side and property handlers correctly
    """

    @staticmethod
    @abstractmethod
    def get_chain_mappings():
        """
        Should return a dictionary containing common property pairs for query mappings.
        This is used to define how to chain results from this query to other possible queries
        """

    @staticmethod
    @abstractmethod
    def get_server_side_handler() -> ServerSideHandler:
        """
        Should return a server-side filter handler object. This object can be used to get filter params to pass to the
        openstacksdk when listing openstack resource objects
        """

    @staticmethod
    @abstractmethod
    def get_client_side_handlers() -> QueryClientSideHandlers:
        """
        Should return a dataclass where each attribute maps to a client-side filter handler. These objects can be used
        to get a filter function to filter a list of openstack resource objects after gathering them using openstacksdk
        command
        """

    @staticmethod
    @abstractmethod
    def get_prop_mapping() -> Type[PropEnum]:
        """
        Returns a mapping of valid presets for server side attributes
        """

    @staticmethod
    @abstractmethod
    def get_runner_mapping() -> Type[RunnerWrapper]:
        """
        Returns a mapping to associated Runner class for the Query
        """
