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

    def __init__(self, prop_enum_cls: Type[PropEnum], runner: QueryRunner):
        self._prop_enum_cls = prop_enum_cls
        self.runner = runner
        self._parser_func = None
        self._output_func = None
        self._client_side_filter_func = None
        self._server_side_filters = None

    def set_filters(
        self,
        client_side_filter_func: Optional[ClientSideFilterFunc] = None,
        server_side_filters: Optional[ServerSideFilters] = None,
    ):
        """
        Setter method for setting run filters
        :param client_side_filter_func: An Optional function used to limit the results after querying openstacksdk
        :param server_side_filters: An Optional set of filter kwargs to pass to openstacksdk
        """
        self._client_side_filter_func = client_side_filter_func
        self._server_side_filters = server_side_filters

    def set_parse_func(
        self,
        parser_func: Optional[
            Callable[[List[OpenstackResourceObj]], Union[Dict, List]]
        ] = None,
    ):
        """
        Setter method for setting parse func
        :param parser_func: A function that takes a list of Openstack Resource Objects and runs parse functions on them
        """
        self._parser_func = parser_func

    def set_output_func(
        self, output_func: Callable[[List[OpenstackResourceObj]], List[Dict[str, str]]]
    ):
        """
        Setter method for setting output func
        :param output_func: A function that takes a list of Openstack Resource Objects and returns a list of
        selected properties (as a dictionary) for each resource given
        """
        self._output_func = output_func

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
        cloud_account: str,
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

        start = time.time()
        results = self.runner.run(
            cloud_account=CloudDomains.from_string(cloud_account).name.lower(),
            client_side_filter_func=self._client_side_filter_func,
            server_side_filters=self._server_side_filters,
            from_subset=from_subset,
            **kwargs,
        )

        logger.debug("run completed - time elapsed: %s seconds", time.time() - start)

        if self._parser_func:
            results = self._parser_func(results)
        return results, self.get_output(results)
