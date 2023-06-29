from abc import abstractmethod

from typing import Optional, Dict, List, Any, Callable

from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.openstack_connection import OpenstackConnection
from custom_types.openstack_query.aliases import OpenstackFilterKwargs, ParsedFilterFunc


class QueryRunner(OpenstackWrapperBase):
    """
    Base class for Runner classes.
    Runner classes encapsulate running any openstacksdk commands
    """

    def __init__(self, connection_cls=OpenstackConnection):
        OpenstackWrapperBase.__init__(self, connection_cls)

    def run(
        self,
        cloud_account: str,
        filter_func: Optional[ParsedFilterFunc] = None,
        filter_kwargs: Optional[OpenstackFilterKwargs] = None,
        from_subset: Optional[List[Any]] = None,
        **kwargs
    ) -> List[Any]:
        """
        Public method that runs the query by querying openstacksdk and then applying a filter function.
        :param cloud_account: The account from the clouds configuration to use
        :param filter_func: An Optional function that we can use to limit the results after querying openstacksdk
        :param filter_kwargs: An Optional set of filter kwargs to limit the results by when querying openstacksdk
        :param from_subset: A subset of openstack resources to run query on instead of querying openstacksdk
        :param kwargs: An extra set of kwargs to pass to internal _run_query method that changes what/how the
        openstacksdk query is run
            - valid kwargs to _run_query is specific to the runner object - see docstrings for _run_query() on the
            runner of interest.
        """

        force_filter_func_usage = False
        with self._connection_cls(cloud_account) as conn:
            if from_subset:
                results_resource_objects = self._parse_subset(conn, from_subset)
                force_filter_func_usage = True
            else:
                results_resource_objects = self._run_query(
                    conn, filter_kwargs, **kwargs
                )

        if filter_kwargs is None or force_filter_func_usage:
            results_resource_objects = self._apply_filter_func(
                results_resource_objects,
                filter_func,
            )
        return results_resource_objects

    @staticmethod
    def _apply_filter_func(
        items: List[Any], filter_func: Callable[[Any], bool]
    ) -> List[Any]:
        """
        Removes items from a list by running a given query function
        :param items: List of items to query e.g. list of servers
        :param filter_func: An Optional function that we can use to limit the results after querying openstacksdk,
            - function takes an openstack resource object and returns True if it passes the filter, false if not
        :return: List of items that match the given query
        """
        return [item for item in items if filter_func(item)]

    @abstractmethod
    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[OpenstackFilterKwargs] = None,
        **kwargs
    ) -> List[Any]:
        """
        This method runs the query by utilising openstacksdk commands. It will set get a list of all available
        resources in question and returns them
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional set of filter kwargs to limit the results by when querying openstacksdk
        :param kwargs: An extra set of kwargs to pass to internal _run_query method that changes what/how the
        openstacksdk query is run
        """

    @abstractmethod
    def _parse_subset(self, conn: OpenstackConnection, subset: List[Any]) -> List[Any]:
        """
        This method is a helper function that will check a subset of openstack objects and check their validity
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param subset: A list of openstack objects to parse
        """
