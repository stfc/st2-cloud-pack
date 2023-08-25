from abc import ABC, abstractmethod
from structs.query.query_client_side_handlers import QueryClientSideHandlers

from openstack_query.handlers.prop_handler import PropHandler
from openstack_query.handlers.server_side_handler import ServerSideHandler

# pylint:disable=too-few-public-methods


class QueryBase(ABC):
    """
    Abstract Base class. This class defines abstract getter methods to enforce Query classes implement
    server-side, client-side and property handlers correctly
    """

    @abstractmethod
    def _get_server_side_handler(self) -> ServerSideHandler:
        """
        Should return a server-side filter handler object. This object can be used to get filter params to pass to the
        openstacksdk when listing openstack resource objects
        """

    @abstractmethod
    def _get_client_side_handlers(self) -> QueryClientSideHandlers:
        """
        Should return a dataclass where each attribute maps to a client-side filter handler. These objects can be used
        to get a filter function to filter a list of openstack resource objects after gathering them using openstacksdk
        command
        """
