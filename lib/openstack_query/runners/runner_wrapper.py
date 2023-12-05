from abc import abstractmethod
from typing import Optional, List, Dict

from custom_types.openstack_query.aliases import (
    PropFunc,
    ServerSideFilters,
    OpenstackResourceObj,
)
from openstack_api.openstack_connection import OpenstackConnection
from exceptions.parse_query_error import ParseQueryError


class RunnerWrapper:
    """
    Base class for Runner classes.
    Runner classes encapsulate running any openstacksdk commands
    """

    RESOURCE_TYPE = type(None)

    def __init__(self, marker_prop_func: PropFunc):
        self._page_marker_prop_func = marker_prop_func

    def parse_subset(
        self, subset: List[OpenstackResourceObj]
    ) -> List[OpenstackResourceObj]:
        """
        This method is a helper function that will check a subset of openstack objects and check their validity
        :param subset: A list of openstack objects to parse
        """

        # connection object may need to be used if we want to run validation checks
        if any(not isinstance(i, self.RESOURCE_TYPE) for i in subset):
            raise ParseQueryError(
                f"'from_subset' only accepts openstack objects of type {self.RESOURCE_TYPE}"
            )
        return subset

    @abstractmethod
    def run_query(
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
    def parse_meta_params(self, conn: OpenstackConnection, **kwargs) -> Dict[str, str]:
        """
        This method is a helper function that will parse a set of meta params specific to the resource and
        return a set of parsed meta-params to pass to _run_query
        """
        return {}
