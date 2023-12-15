from typing import Callable, Optional, List
import logging

from custom_types.openstack_query.aliases import (
    ServerSideFilter,
    ClientSideFilters,
    ClientSideFilterFunc,
)

logger = logging.getLogger(__name__)


class RunnerUtils:
    """
    A helper class which holds utility functions for Runner classes
    """

    @staticmethod
    def run_paginated_query(
        paginated_call: Callable,
        marker_prop_func: Callable,
        server_side_filter_set: Optional[ServerSideFilter] = None,
        page_size=1000,
        call_limit=1000,
    ):
        """
        Helper method for running a query using pagination - openstacksdk calls usually return a maximum number of
        values - (set by limit) and to continue getting values we can pass a "marker" value of the last item seen to
        continue the query - this speeds up the time needed to run queries
        :param paginated_call: A function which takes a openstacksdk call which allows limit and marker to be set
        :param marker_prop_func: A function which takes a openstack resource object and return value of a property
        that can be used as a marker for pagination
        :param server_side_filter_set: A set of filters to pass to openstacksdk call
        :param page_size: (Default 1000) how many items are returned by single call
        :param call_limit: (Default 1000) max number of paging iterations.
            - this is required to mitigate some bugs where successive paging loops back on itself
            leading to endless calls
        """

        paginated_filters = {"limit": page_size, "marker": None}
        paginated_filters.update(server_side_filter_set)
        query_res = []

        curr_marker = None
        num_calls = 1
        while True:
            logger.debug("starting page loop, completed %s loops", num_calls)
            num_calls += 1
            if num_calls > call_limit:
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
                if i == page_size - 1:
                    # restart the for loop with marker set
                    paginated_filters.update({"marker": marker_prop_func(resource)})
                    logger.debug(
                        "page limit reached: %s - setting new marker: %s",
                        page_size,
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
    def apply_client_side_filters(items: List, filters: ClientSideFilters):
        """
        Removes items from a list by running a given filter functions
        :param items: List of items to query e.g. list of servers
        :param filters: filter functions that we can use to limit the results after querying openstacksdk,
            - each function takes an openstack resource object and returns True if it passes the filter, false if not
        :return: List of items that match the1 given query
        """
        for client_filter in filters:
            items = RunnerUtils._apply_client_side_filter(items, client_filter)
        return items

    @staticmethod
    def _apply_client_side_filter(
        items: List, client_filter: ClientSideFilterFunc
    ) -> Optional[List]:
        """
        Method that will apply a client filter on a list of openstack items
        :param items: A list of openstack resources
        :param client_filter: A client filter to apply
        """
        return [item for item in items if client_filter(item) is True]
