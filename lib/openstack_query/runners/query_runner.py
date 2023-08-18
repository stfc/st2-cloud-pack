from abc import abstractmethod
from typing import Optional, List, Any
import time
import logging

from enums.cloud_domains import CloudDomains

from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.openstack_connection import OpenstackConnection
from custom_types.openstack_query.aliases import (
    ServerSideFilters,
    ClientSideFilterFunc,
    OpenstackResourceObj,
)

logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods


class QueryRunner(OpenstackWrapperBase):
    """
    Base class for Runner classes.
    Runner classes encapsulate running any openstacksdk commands
    """

    def __init__(self, connection_cls=OpenstackConnection):
        OpenstackWrapperBase.__init__(self, connection_cls)

    def run(
        self,
        cloud_account: CloudDomains,
        client_side_filter_func: Optional[ClientSideFilterFunc] = None,
        server_side_filters: Optional[ServerSideFilters] = None,
        from_subset: Optional[List[Any]] = None,
        **kwargs,
    ) -> List[OpenstackResourceObj]:
        """
        Public method that runs the query by querying openstacksdk and then applying a filter function.
        :param cloud_account: An Enum for the account from the clouds configuration to use
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
        with self._connection_cls(cloud_account.name.lower()) as conn:
            logger.debug(
                "openstack connection established - using cloud account '%s'",
                cloud_account.name.lower(),
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
                resource_objects = self._run_query(conn, server_side_filters, **kwargs)
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
        :param kwargs: An extra set of kwargs to pass to internal _run_query method that changes what/how the
        openstacksdk query is run
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
