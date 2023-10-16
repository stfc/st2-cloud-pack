from typing import Tuple, List, Optional

from enums.query.props.prop_enum import PropEnum
from enums.query.query_types import QueryTypes


class QueryChainer:
    """
    Helper class to handle chaining queries together
    """

    def __init__(self, chain_mappings):
        self._chain_mappings = chain_mappings

    def get_supported_queries(self) -> List[QueryTypes]:
        """
        Gets a list of all supported query types that this query can be chained into
        """
        return list(self._chain_mappings.keys())

    def check_supported(self, query: QueryTypes) -> bool:
        """
        Checks whether this query can be chained into a given query
        :param query: QueryTypes enum representing the query to check if chaining is supported for
        """
        return query in self._chain_mappings.keys()

    def get_link_props(self, query: QueryTypes) -> Optional[Tuple[PropEnum, PropEnum]]:
        """
        Get the link property pair to use to convert from current query to new query
        (if mapping exists)
        :param query: QueryTypes enum representing the query to get link properties for
        """
        if not self.check_supported(query):
            return None
        return self._chain_mappings[query]
