import time
import logging
from typing import Optional, Dict, List, Any, Union, Type

from openstack_query.query_blocks.results_container import ResultsContainer
from openstack_query.runners.runner_wrapper import RunnerWrapper
from enums.cloud_domains import CloudDomains
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
    ):
        self._results_container = ResultsContainer(prop_enum_cls)
        self.runner = runner_cls(prop_enum_cls.get_marker_prop_func())
        self._client_side_filters = None
        self._server_side_filters = None
        self.has_forwarded_results = False

    @property
    def results_container(self) -> ResultsContainer:
        """
        a getter method for results container object holding query results
        """
        return self._results_container

    @property
    def client_side_filters(self):
        """
        a getter method to return the client-side filter function
        """
        return self._client_side_filters

    @client_side_filters.setter
    def client_side_filters(self, client_filters=ClientSideFilters):
        """
        Setter method for setting run filters
        :param client_filters: a list of filter functions that each take an openstack resource
        and returns True if it matches filter, False if not
        """
        self._client_side_filters = client_filters

    @property
    def server_side_filters(self):
        """
        a getter method to return the server side filter functions
        """
        return self._server_side_filters

    @server_side_filters.setter
    def server_side_filters(self, server_filters: ServerSideFilters):
        """
        a setter method to return the server side filter functions
        :param server_filters: A dictionary of filter kwargs to pass to openstacksdk
        """
        self._server_side_filters = server_filters

    def run_query(
        self,
        cloud_account: Union[str, CloudDomains],
        from_subset: Optional[List[Any]] = None,
        **kwargs,
    ):
        """
        method that runs the query provided and outputs
        :param cloud_account: An Enum for the account from the clouds configuration to use
        :param from_subset: A subset of openstack resources to run query on instead of querying openstacksdk
        :param kwargs: An extra set of kwargs to pass to internal _run_query method that changes what/how the
        openstacksdk query is run
            - valid kwargs to _run_query is specific to the runner object - see docstrings for _run_query() on the
            runner of interest.
        """

        if isinstance(cloud_account, CloudDomains):
            cloud_account = cloud_account.name.lower()

        start = time.time()

        self.results_container.store_query_results(
            self.runner.run(
                cloud_account=cloud_account,
                client_side_filters=self.client_side_filters,
                server_side_filters=self.server_side_filters,
                from_subset=from_subset,
                **kwargs,
            )
        )
        logger.debug("run completed - time elapsed: %s seconds", time.time() - start)

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
