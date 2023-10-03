import time
import logging
from typing import Callable, Optional, Dict, List, Any, Union, Type

from openstack_query.runners.runner_wrapper import RunnerWrapper
from enums.cloud_domains import CloudDomains
from enums.query.props.prop_enum import PropEnum

from custom_types.openstack_query.aliases import (
    OpenstackResourceObj,
    ServerSideFilters,
    ClientSideFilters,
)

logger = logging.getLogger(__name__)


class QueryExecuter:
    """
    Helper class to handle executing the query - primarily performing 'run()' method
    """

    def __init__(self, prop_enum_cls: Type[PropEnum], runner_cls: Type[RunnerWrapper]):
        self._prop_enum_cls = prop_enum_cls
        self.runner = runner_cls(self._prop_enum_cls.get_marker_prop_func())
        self._parse_func = None
        self._output_func = None
        self._client_side_filters = None
        self._server_side_filters = None

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
    def parse_func(self):
        """
        a getter method for parse function
        """
        return self._parse_func

    @parse_func.setter
    def parse_func(
        self,
        parse_func: Optional[Callable[[List[OpenstackResourceObj]], Union[Dict, List]]],
    ):
        """
        Setter method for setting parse function
        :param parse_func: A function that takes a list of Openstack Resource Objects and runs parse functions on them
        """
        self._parse_func = parse_func

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
        if not self.output_func:
            return []

        if not isinstance(results, dict):
            return self.output_func(results)

        return {name: self.output_func(group) for name, group in results.items()}

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

        logger.debug("run completed - time elapsed: %s seconds", time.time() - start)

        if self.parse_func:
            results = self.parse_func(results)
        return results, self.get_output(results)
