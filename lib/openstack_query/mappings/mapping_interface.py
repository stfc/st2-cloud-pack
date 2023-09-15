import abc
from typing import Type

from enums.query.props.prop_enum import PropEnum
from openstack_query.handlers.server_side_handler import ServerSideHandler
from structs.query.query_client_side_handlers import QueryClientSideHandlers


class MappingInterface(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def get_prop_mapping() -> Type[PropEnum]:
        """
        Returns a mapping of valid presets for server side attributes
        """

    @staticmethod
    @abc.abstractmethod
    def get_server_side_handler() -> ServerSideHandler:
        """
        Returns a mapping of valid presets for server side attributes
        """

    @staticmethod
    @abc.abstractmethod
    def get_client_side_handlers() -> QueryClientSideHandlers:
        """
        Returns a mapping of valid presets for client side attributes
        """
