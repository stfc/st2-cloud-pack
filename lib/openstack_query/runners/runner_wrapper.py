import logging
import time
from abc import abstractmethod
from typing import Optional, List, Any, Dict, Callable

from custom_types.openstack_query.aliases import (
    PropFunc,
    ServerSideFilters,
    ClientSideFilterFunc,
    OpenstackResourceObj,
)
from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase

logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods


class RunnerWrapper(OpenstackWrapperBase):
    """
    Base class for Runner classes.
    Runner classes encapsulate running any openstacksdk commands
    """

    # Sets the limit for getting values from openstack
    _LIMIT_FOR_PAGINATION = 1000
    _PAGINATION_CALL_LIMIT = 1000

    def __init__(self, marker_prop_func: PropFunc, connection_cls=OpenstackConnection):
        OpenstackWrapperBase.__init__(self, connection_cls)
        self._page_marker_prop_func = marker_prop_func

    def run(
        self,
        cloud_account: str,
        client_side_filter_func: Optional[ClientSideFilterFunc] = None,
        server_side_filters: Optional[ServerSideFilters] = None,
        from_subset: Optional[List[Any]] = None,
        **kwargs,
    ) -> List[OpenstackResourceObj]:
        """
        Public method that runs the query by querying openstacksdk and then applying a filter function.
        :param cloud_account: An string for the account from the clouds configuration to use
        :param client_side_filter_func: An Optional function that we can use to limit the results after querying
        openstacksdk
        :param server_side_filters: An Optional set of filter kwargs to limit the results by when querying openstacksdk
        :param from_subset: A subset of openstack resources to run query on instead of querying openstacksdk
        :param kwargs: An extra set of kwargs to pass to internal _run_query method that changes what/how the
        openstacksdk query is run
            - valid kwargs to _run_query is specific to the runner object - see docstrings for _run_query() on the
            runner of interest.
        """
        logger.debug("making connection to openstack")
        with self._connection_cls(cloud_account) as conn:
            logger.debug(
                "openstack connection established - using cloud account '%s'",
                cloud_account,
            )

            if from_subset:
                logger.info("'from_subset' meta param given - parsing subset")
                logger.debug("parsing subset of %s items", len(from_subset))
                start = time.time()
                resource_objects = self._parse_subset(conn, from_subset)
                logger.debug(
                    "parsing complete - time elapsed: %s seconds", time.time() - start
                )
            else:
                logger.info("running query using openstacksdk and server-side filters")
                server_side_filters_log_str = "none (getting all)"
                kwarg_log_str = "none"
                if server_side_filters:
                    server_side_filters_log_str = "\n\t\t".join(
                        [f"{key}: '{val}'" for key, val in server_side_filters.items()]
                    )
                if kwargs:
                    kwarg_log_str = "\n\t\t".join(
                        [f"{key}: '{val}'" for key, val in kwargs.items()]
                    )

                logger.debug(
                    "calling run_query with parameters "
                    "\n\tserver_side_filters: "
                    "\n\t\t%s "
                    "\n\trun_meta_kwargs: "
                    "\n\t\t%s",
                    server_side_filters_log_str,
                    kwarg_log_str,
                )
                start = time.time()
                query_meta_params = {}
                if kwargs:
                    query_meta_params = self._parse_meta_params(conn, **kwargs)
                resource_objects = self._run_query(
                    conn, server_side_filters, **query_meta_params
                )
                logger.info(
                    "server-side query complete - time elapsed: %s seconds",
                    time.time() - start,
                )
                logger.debug("server-side query found %s items", len(resource_objects))

        if client_side_filter_func and not server_side_filters:
            logger.info("applying client side filters")
            resource_objects = self._apply_client_side_filter(
                resource_objects, client_side_filter_func
            )

        logger.info("found %s items in total", len(resource_objects))
        return resource_objects

    def _run_paginated_query(
        self,
        paginated_call: Callable,
        server_side_filters: Optional[ServerSideFilters] = None,
    ):
        """
        Helper method for running a query using pagination - openstacksdk calls usually return a maximum number of
        values - (set by limit) and to continue getting values we can pass a "marker" value of the last item seen to
        continue the query - this speeds up the time needed to run queries
        :param paginated_call: A lambda function which takes a openstacksdk call which allows limit and marker to be set
        :param server_side_filters: A set of filters to pass to openstacksdk call
        """

        paginated_filters = {"limit": self._LIMIT_FOR_PAGINATION, "marker": None}
        paginated_filters.update(server_side_filters)
        query_res = []

        curr_marker = None
        num_calls = 1
        while True:
            logger.debug("starting page loop, completed %s loops", num_calls)
            num_calls += 1
            if num_calls > self._PAGINATION_CALL_LIMIT:
                logger.warning(
                    "max page loops reached %s - terminating early", num_calls
                )
                break

            prev = None
            for i, resource in enumerate(paginated_call(**paginated_filters)):
                # Workaround for Endless loop error detected if querying for stfc users (via ldap)
                # for loop doesn't seem to terminate - and outputs the same value when given "limit" and "marker"
                if prev == resource:
                    logger.warning(
                        "duplicate entries found, likely an endless page loop - terminating early"
                    )
                    break

                query_res.append(resource)
                # openstacksdk calls break after going over pagination limit
                if i == self._LIMIT_FOR_PAGINATION - 1:
                    # restart the for loop with marker set
                    paginated_filters.update(
                        {"marker": self._page_marker_prop_func(resource)}
                    )
                    logger.debug(
                        "page limit reached: %s - setting new marker: %s",
                        self._LIMIT_FOR_PAGINATION,
                        paginated_filters["marker"],
                    )
                    break

                prev = resource

            # if marker hasn't changed, then has query terminated
            if not paginated_filters or paginated_filters["marker"] == curr_marker:
                logger.debug("page loop terminated")
                break
            # set marker as current
            curr_marker = paginated_filters["marker"]
        return query_res

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
        **kwargs,
    ) -> List[OpenstackResourceObj]:
        """
        This method runs the query by utilising openstacksdk commands. It will set get a list of all available
        resources in question and returns them
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional set of filter kwargs to limit the results by when querying openstacksdk
        :param kwargs: An extra set of meta params to pass to internal _run_query method that changes what/how the
        openstacksdk query is run - these kwargs are specific to the resource runner.
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

    @abstractmethod
    def _parse_meta_params(self, conn: OpenstackConnection, **kwargs) -> Dict[str, str]:
        """
        This method is a helper function that will parse a set of meta params specific to the resource and
        return a set of parsed meta-params to pass to _run_query
        """
