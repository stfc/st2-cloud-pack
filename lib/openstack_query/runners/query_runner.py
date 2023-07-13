from abc import abstractmethod
from typing import Optional, List, Any, Callable

from enums.cloud_domains import CloudDomains

from exceptions.parse_query_error import ParseQueryError
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.openstack_connection import OpenstackConnection
from custom_types.openstack_query.aliases import (
    ServerSideFilters,
    ClientSideFilterFunc,
    OpenstackResourceObj,
)

# pylint:disable=too-few-public-methods


class QueryRunner(OpenstackWrapperBase):
    """
    Base class for Runner classes.
    Runner classes encapsulate running any openstacksdk commands
    """

    def __init__(self, connection_cls=OpenstackConnection):
        OpenstackWrapperBase.__init__(self, connection_cls)

    def run(
        self,
        cloud_account: CloudDomains,
        client_side_filter_func: Optional[ClientSideFilterFunc] = None,
        server_side_filters: Optional[ServerSideFilters] = None,
        from_subset: Optional[List[Any]] = None,
        **kwargs
    ) -> List[OpenstackResourceObj]:
        """
        Public method that runs the query by querying openstacksdk and then applying a filter function.
        :param cloud_account: An Enum for the account from the clouds configuration to use
        :param client_side_filter_func: An Optional function that we can use to limit the results after querying
        openstacksdk
        :param server_side_filters: An Optional set of filter kwargs to limit the results by when querying openstacksdk
        :param from_subset: A subset of openstack resources to run query on instead of querying openstacksdk
        :param kwargs: An extra set of kwargs to pass to internal _run_query method that changes what/how the
        openstacksdk query is run
            - valid kwargs to _run_query is specific to the runner object - see docstrings for _run_query() on the
            runner of interest.
        """

        with self._connection_cls(cloud_account.name.lower()) as conn:
            resource_objects = (
                self._parse_subset(conn, from_subset)
                if from_subset
                else self._run_query(conn, server_side_filters, **kwargs)
            )

        if client_side_filter_func and not server_side_filters:
            resource_objects = self._apply_client_side_filter(
                resource_objects, client_side_filter_func
            )
        return resource_objects

    @staticmethod
    def _apply_client_side_filter(
        items: List[OpenstackResourceObj], filter_func: ClientSideFilterFunc
    ) -> List[OpenstackResourceObj]:
        """
        Removes items from a list by running a given filter function
        :param items: List of items to query e.g. list of servers
        :param filter_func: An Optional function that we can use to limit the results after querying openstacksdk,
            - function takes an openstack resource object and returns True if it passes the filter, false if not
        :return: List of items that match the1 given query
        """
        return [item for item in items if filter_func(item)]

    @abstractmethod
    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[ServerSideFilters] = None,
        **kwargs
    ) -> List[OpenstackResourceObj]:
        """
        This method runs the query by utilising openstacksdk commands. It will set get a list of all available
        resources in question and returns them
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional set of filter kwargs to limit the results by when querying openstacksdk
        :param kwargs: An extra set of kwargs to pass to internal _run_query method that changes what/how the
        openstacksdk query is run
        """

    @abstractmethod
    def _parse_subset(
        self, conn: OpenstackConnection, subset: List[OpenstackResourceObj]
    ) -> List[OpenstackResourceObj]:
        """
        This method is a helper function that will check a subset of openstack objects and check their validity
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param subset: A list of openstack objects to parse
        """
