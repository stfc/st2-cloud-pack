from typing import List, Tuple, Dict, Callable
from custom_types.openstack_query.aliases import OpenstackResourceObj, PropValue


class ResultsContainer:
    """
    Helper class to store query results and forwarded results
    """

    def __init__(self):
        self._results: List[Tuple[OpenstackResourceObj, Dict]] = []

    def output(self) -> List[Tuple[OpenstackResourceObj, Dict]]:
        """
        output the results stored
        """
        return self._results

    def set_from_query_results(self, query_results: List[OpenstackResourceObj]):
        """
        a setter to set results after running the query with query results
        :param query_results: A list of openstack objects returned after running query
        """
        # initialise with no forwarded outputs set
        self._results = [(result, {}) for result in query_results]

    def apply_forwarded_results(
        self,
        link_prop_func: Callable[[OpenstackResourceObj], PropValue],
        forwarded_results: Dict[PropValue, List[Dict]],
    ):
        """
        public method that when called will concatenate forwarded results onto each result.
        :param forwarded_results: a grouped set of forwarded results, grouped by a common property
        :param link_prop_func: a function that takes a openstack resource object and computes its value for shared
        common property to be used to attach appropriate forwarded result
        """
        if not self._results:
            return

        self._results = [
            (
                tup[0],
                {
                    **tup[1],
                    **self._get_forwarded_result(
                        link_prop_func(tup[0]), forwarded_results
                    ),
                },
            )
            for tup in self._results
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
