import logging
import time
from typing import Optional, Dict, List, Type

from openstack_query.query_blocks.results_container import ResultsContainer
from openstack_query.runners.runner_wrapper import RunnerWrapper
from openstack_query.runners.runner_utils import RunnerUtils

from openstack_api.openstack_connection import OpenstackConnection

from enums.query.props.prop_enum import PropEnum

from custom_types.openstack_query.aliases import (
    ServerSideFilters,
    ClientSideFilters,
    PropValue,
)

logger = logging.getLogger(__name__)


# pylint:disable=too-many-instance-attributes


class QueryExecuter:
    """
    Helper class to handle executing the query - primarily performing 'run()' method
    """

    def __init__(
        self,
        prop_enum_cls: Type[PropEnum],
        runner_cls: Type[RunnerWrapper],
        connection_cls=OpenstackConnection,
    ):
        self._results_container = ResultsContainer(prop_enum_cls)
        self._connection_cls = connection_cls
        self.runner = runner_cls(prop_enum_cls.get_marker_prop_func())
        self.has_forwarded_results = False

    @property
    def results_container(self) -> ResultsContainer:
        """
        a getter method for results container object holding query results
        """
        return self._results_container

    def apply_forwarded_results(
        self, link_prop: PropEnum, forwarded_results: Dict[PropValue, List[Dict]]
    ):
        """
        public method that attaches forwarded results to results stored in result container.
        :param forwarded_results: A set of grouped results forwarded from a previous query to attach to results
        :param link_prop: An prop enum that the forwarded results are grouped by
        """
        self.has_forwarded_results = True
        self.results_container.apply_forwarded_results(link_prop, forwarded_results)

    def run_with_openstacksdk(
        self,
        cloud_account: str,
        client_side_filters: Optional[ClientSideFilters] = None,
        server_side_filters: Optional[ServerSideFilters] = None,
        **kwargs,
    ):
        """
        public method that runs the query by querying openstacksdk using the Runner class stored one or more times
        and then applying any client-side filter function(s).
        :param cloud_account: A string for the account from the clouds configuration to use
        :param client_side_filters: An Optional list of filter functions to run locally that we can use to limit the
        results after querying openstacksdk
        :param server_side_filters: An Optional list of filter kwargs to limit the results by when querying openstacksdk
        :param kwargs: An extra set of kwargs to pass to internal _run_query method that changes what/how the
        openstacksdk query is run
            - valid kwargs to _run_query is specific to the runner object - see docstrings for _run_query() on the
            runner of interest.
        """
        if not server_side_filters:
            server_side_filters = [None]

        start = time.time()
        resource_objects = []
        with self._connection_cls(cloud_account) as conn:
            logger.debug(
                "openstack connection established - using cloud account '%s'",
                cloud_account,
            )
            meta_params = self.runner.parse_meta_params(conn, **kwargs)
            for i, query_filters in enumerate(server_side_filters, 1):
                logger.debug("running query %s / %s", i, len(server_side_filters))
                resource_objects.extend(
                    self.runner.run_query(conn, query_filters, **meta_params)
                )

        if client_side_filters:
            resource_objects = RunnerUtils.apply_client_side_filters(
                resource_objects, client_side_filters
            )
        logger.info(
            "Query Complete! Found %s items. Time elapsed: %0.4f seconds",
            len(resource_objects),
            time.time() - start,
        )

        self.results_container.store_query_results(resource_objects)

    def run_with_subset(self, subset: List, client_side_filters: ClientSideFilters):
        """
        Public method that runs the query when provided a subset. This will apply client-side filter functions
        on the subset without needing to query using the sdk
        :param subset: A subset of openstack resources to run query on instead of querying openstacksdk
        :param client_side_filters: A list of filter functions to apply
        """
        logger.info("'from_subset' meta param given - running query on subset")
        start = time.time()

        subset = self.runner.parse_subset(subset)

        resource_objects = RunnerUtils.apply_client_side_filters(
            items=subset, filters=client_side_filters
        )

        logger.info(
            "Query Complete! Found %s items. Time elapsed: %0.4f seconds",
            len(resource_objects),
            time.time() - start,
        )
        self.results_container.store_query_results(resource_objects)
