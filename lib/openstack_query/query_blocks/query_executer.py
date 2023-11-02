import copy
import time
import logging
from typing import Tuple, Callable, Optional, Dict, List, Any, Union, Type

from openstack_query.runners.runner_wrapper import RunnerWrapper
from enums.cloud_domains import CloudDomains
from enums.query.props.prop_enum import PropEnum

from custom_types.openstack_query.aliases import (
    OpenstackResourceObj,
    ServerSideFilters,
    ClientSideFilters,
    PropValue,
)

logger = logging.getLogger(__name__)


# pylint:disable=too-many-instance-attributes
# TODO: streamline these instance attributes later


class QueryExecuter:
    """
    Helper class to handle executing the query - primarily performing 'run()' method
    """

    def __init__(self, prop_enum_cls: Type[PropEnum], runner_cls: Type[RunnerWrapper]):
        self._prop_enum_cls = prop_enum_cls
        self.runner = runner_cls(self._prop_enum_cls.get_marker_prop_func())
        self._client_side_filters = None
        self._server_side_filters = None
        self._results: List[Tuple[OpenstackResourceObj, Dict]] = []

        # for chaining
        self._forwarded_values = {}
        self._link_prop_func = lambda a: None

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

    @property
    def results(self) -> List[OpenstackResourceObj]:
        """
        a getter for raw results
        """
        return self._results

    @results.setter
    def results(self, results: List[OpenstackResourceObj]):
        """
        a setter for raw results
        """
        self._results = results

    @property
    def forwarded_values(self) -> Dict[PropValue, List]:
        """
        a getter for forwarded results from previous queries
        """
        return self._forwarded_values

    @property
    def link_prop_func(self) -> Callable[[OpenstackResourceObj], PropValue]:
        """
        a getter for function to return link prop
        """
        return self._link_prop_func

    def set_forwarded_values(
        self,
        link_prop_func: Callable[[OpenstackResourceObj], PropValue],
        forwarded_values: Dict[PropValue, List],
    ):
        """
        a setter for setting forwarded results from link prop func
        """
        self._link_prop_func = link_prop_func
        self._forwarded_values = forwarded_values

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
        results = self.runner.run(
            cloud_account=cloud_account,
            client_side_filters=self.client_side_filters,
            server_side_filters=self.server_side_filters,
            from_subset=from_subset,
            **kwargs,
        )

        self.results = [(result, {}) for result in results]
        logger.debug("run completed - time elapsed: %s seconds", time.time() - start)

    def apply_forwarded_results(
        self, forwarded_results: Dict[PropValue, List[Dict]], link_prop_func
    ):
        """
        public method that when called will concatenate forwarded results onto each result.
        :param forwarded_results: a grouped set of forwarded results, grouped by a common property
        :param link_prop_func: a function that takes a openstack resource object and computes its value for shared
        common property to be used to attach appropriate forwarded result
        """
        if not self.results:
            return

        self.results = [
            (
                tup[0],
                {
                    **tup[1],
                    **self._get_forwarded_result(
                        link_prop_func(tup[0]), forwarded_results
                    ),
                },
            )
            for tup in self.results
        ]

    @staticmethod
    def _get_forwarded_result(prop_val: str, forwarded_results: Dict[str, List]):
        """
        static helper method to return forwarded values that match a given property value. Used for chaining
        This handles two chaining cases:
            - many-to-one (or one-to-one as we're using duplicates)
                - where multiple forwarded outputs maps to one openstack object in result
                - the result will contain exact number of duplicate openstack objects so each forwarded output is
                assigned to an appropriate copy

            - one-to-many - where one forwarded output needs to map to multiple openstack objects in results

        :param prop_val: common property value to use to find a set of forwarded values to return
        :param forwarded_results: a grouped dictionary which holds forwarded values grouped by common property value
        """

        if not forwarded_results:
            return {}

        result_to_attach = forwarded_results[prop_val][0]

        # if forwarded_results group contains only one item:
        #   - we assume we're chaining a one-to-many and keep at least one value

        # if it contains multiple item:
        #   - we assume many-to-one and delete the value

        # deleting is a nice way of making sure each value is set - otherwise we need to keep track
        # of the index position of last read item for each group
        if len(forwarded_results[prop_val]) > 1:
            del forwarded_results[prop_val][0]

        return result_to_attach

    def parse_results(
        self,
        parse_func: Optional[Callable],
        output_func: Optional[Callable],
    ) -> Tuple[Union[List, Dict], Union[List, Dict]]:
        """
        This method takes the results computed in run_query() and applies the pre-set parser
        and generate output functions - outputs results as object list/dict and as selected props list/dict
        (including forwarded outputs)
        :param parse_func: function that groups and sorts object results
        :param output_func: function that takes object results and converts it into selected outputs
        """
        results = self._results
        if parse_func:
            results = parse_func(self._results)

        if not isinstance(results, dict):
            as_object_results = [result[0] for result in results]
        else:
            as_object_results = {
                name: [result[0] for result in group] for name, group in results.items()
            }

        as_prop_results = self.get_output(output_func, results)

        return as_object_results, as_prop_results

    @staticmethod
    def get_output(
        output_func: Optional[Callable],
        results: List[Tuple[OpenstackResourceObj, Dict]],
    ):
        """
        Helper method for getting the output using output func
        :param output_func: function that takes raw results and returns parsed outputs
        :param results: Either a list or group of Openstack Resource objects
        """
        if not output_func:
            return []

        if not isinstance(results, dict):
            return output_func(results)

        return {name: output_func(group) for name, group in results.items()}
