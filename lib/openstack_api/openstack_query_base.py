from abc import abstractmethod
from typing import Dict, Callable, Any

from openstack_api.dataclasses import QueryParams
from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_query import OpenstackQuery


class OpenstackQueryBase:
    """
    Base class for Openstack API wrappers to obtain query functionality
    """

    _query_api: OpenstackQuery

    def __init__(self, connection_cls=OpenstackConnection):
        self._query_api = OpenstackQuery(connection_cls)

    def __getitem__(self, item):
        """
        Implemented to allow 'search_' functions to be called using array notation
        """
        return getattr(self, item)

    @abstractmethod
    def get_query_property_funcs(
        self, cloud_account: str
    ) -> Dict[str, Callable[[Any], Any]]:
        """
        Should return property functions for use with OpenstackQuery.parse_properties
        :param cloud_account: The associated clouds.yaml account
        """

    def search(self, cloud_account: str, query_params: QueryParams, **kwargs):
        """
        Performs a search of a resource and returns a table of results
        :param cloud_account: The associated clouds.yaml account
        :param query_params: See QueryParams
        """
        return self._query_api.search_resource(
            cloud_account=cloud_account,
            search_api=self,
            property_funcs=self.get_query_property_funcs(cloud_account),
            query_params=query_params,
            **kwargs,
        )
