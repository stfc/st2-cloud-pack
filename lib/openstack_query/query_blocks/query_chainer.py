from typing import Tuple, List, Optional, Union

from enums.query.props.prop_enum import PropEnum
from enums.query.query_presets import QueryPresetsGeneric
from enums.query.query_types import QueryTypes
from exceptions.query_chaining_error import QueryChainingError


class QueryChainer:
    """
    Helper class to handle chaining queries together
    """

    def __init__(self, chain_mappings):
        self._chain_mappings = chain_mappings

    def get_chaining_props(self) -> List[QueryTypes]:
        """
        Gets a list of all supported props that can be used to chain to other queries
        """
        return list(self._chain_mappings.keys())

    def check_prop_supported(self, prop: PropEnum) -> bool:
        """
        Checks whether a prop can be used as a link prop for the query
        :param prop: prop to check if it is a chain prop for given query
        """
        return prop in self._chain_mappings.keys()

    def get_link_props(
        self, next_query: QueryTypes
    ) -> Optional[Tuple[PropEnum, PropEnum]]:
        """
        Get the link property pair to use to convert from current query to new query
        (if mapping exists)
        :param next_query: next Query QueryTypes
        """

        new_query_props = next_query.value.get_prop_mapping()
        for start_chain_prop, check_prop in self._chain_mappings.items():
            if check_prop in new_query_props:
                return start_chain_prop, check_prop
        return None

    @staticmethod
    def parse_then(
        current_query,
        query_type: Union[str, QueryTypes],
        keep_previous_results: bool = False,
    ):
        """
        Public static method to chain current query into another query of a different type
        and return the new query so that it will work only on the results of the original query.
        :param current_query: current QueryAPI object
        :param query_type: an enum representing the new query to chain into
        :param keep_previous_results: boolean that if true - will forward outputs from
        this query (and previous chained queries) onto new query.
        """

        # prevents circular imports
        # pylint:disable=import-outside-toplevel
        from openstack_query.query_factory import QueryFactory
        from openstack_query.api.query_api import QueryAPI

        if isinstance(query_type, str):
            query_type = QueryTypes.from_string(query_type)

        link_props = current_query.chainer.get_link_props(query_type)
        if not link_props:
            raise QueryChainingError(
                f"Query Chaining Error: Could not find a way to chain current query into {query_type}"
            )

        # we group the current results by the link property as this is the way we forward results
        current_query_results = current_query.group_by(link_props[0]).to_props()
        if not current_query_results:
            raise QueryChainingError(
                "Query Chaining Error: No values found after running this query - aborting. "
                "Have you run the query first?"
            )

        to_forward = None
        if keep_previous_results:
            to_forward = (link_props[1], current_query_results)

        new_query = QueryAPI(
            QueryFactory.build_query_deps(query_type.value, to_forward)
        )
        return new_query.where(
            QueryPresetsGeneric.ANY_IN,
            link_props[1],
            values=list(current_query_results.keys()),
        )
