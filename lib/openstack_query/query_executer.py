import time
import logging
from typing import Callable, Optional, Dict, List, Any, Union, Type

from openstack_query.runners.query_runner import QueryRunner
from enums.cloud_domains import CloudDomains
from enums.query.props.prop_enum import PropEnum

from custom_types.openstack_query.aliases import (
    OpenstackResourceObj,
    ServerSideFilters,
    ClientSideFilterFunc,
)

logger = logging.getLogger(__name__)


class QueryExecuter:
    """
    Helper class to handle executing the query - primarily performing 'run()' method
    """

    def __init__(self, prop_enum_cls: Type[PropEnum], runner_cls: Type[QueryRunner]):
        self._prop_enum_cls = prop_enum_cls
        self.runner = runner_cls(self._prop_enum_cls.get_marker_prop_func())
        self._parse_func = None
        self._output_func = None
        self._client_side_filter_func = None
        self._server_side_filters = None

    @property
    def client_side_filter_func(self):
        return self._client_side_filter_func

    @client_side_filter_func.setter
    def client_side_filter_func(self, val: ClientSideFilterFunc):
        """
        Setter method for setting run filters
        :param val: An function used to limit the results after querying openstacksdk
        """
        self._client_side_filter_func = val

    @property
    def server_side_filters(self):
        return self._server_side_filters

    @server_side_filters.setter
    def server_side_filters(self, val: ServerSideFilters):
        self._server_side_filters = val

    @property
    def parse_func(self):
        return self._parse_func

    @parse_func.setter
    def parse_func(
        self, val: Optional[Callable[[List[OpenstackResourceObj]], Union[Dict, List]]]
    ):
        """
        Setter method for setting parse func
        :param val: A function that takes a list of Openstack Resource Objects and runs parse functions on them
        """
        self._parse_func = val

    @property
    def output_func(self):
        return self._output_func

    @output_func.setter
    def output_func(
        self, val: Callable[[List[OpenstackResourceObj]], List[Dict[str, str]]]
    ):
        """
        Setter method for setting output func
        :param val: A function that takes a list of Openstack Resource Objects and returns a list of
        selected properties (as a dictionary) for each resource given
        """
        self._output_func = val

    def get_output(
        self,
        results: Union[
            List[OpenstackResourceObj], Dict[str, List[OpenstackResourceObj]]
        ],
    ):
        """
        Helper method for getting the output using output func
        :param results: Either a list or group of Openstack Resource objects
        """
        if not self._output_func:
            return []

        if not isinstance(results, dict):
            return self._output_func(results)

        return {name: self._output_func(group) for name, group in results.items()}

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
            client_side_filter_func=self._client_side_filter_func,
            server_side_filters=self._server_side_filters,
            from_subset=from_subset,
            **kwargs,
        )

        logger.debug("run completed - time elapsed: %s seconds", time.time() - start)

        if self._parse_func:
            parse_func = self._parse_func
            results = parse_func(results)
        return results, self.get_output(results)
