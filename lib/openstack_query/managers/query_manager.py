from typing import Optional, Set, Any, List, Union, Dict

from enums.query.query_output_types import QueryOutputTypes
from enums.query.props.prop_enum import PropEnum


from structs.query.query_output_details import QueryOutputDetails
from structs.query.query_preset_details import QueryPresetDetails

from openstack_query.queries.query_wrapper import QueryWrapper

QueryReturn = Union[str, List[Any]]


class QueryManager:
    """
    This class is the base class for all managers.
    Managers hold a query object and several methods which build and run specific queries
    """

    def __init__(self, query: QueryWrapper, cloud_account: str):
        self._query = query
        self._cloud_account = cloud_account

    def _build_and_run_query(
        self,
        preset_details: QueryPresetDetails,
        output_details: QueryOutputDetails,
    ):
        """
        method to build the query, execute it, and return the results
        :param preset_details: A dataclass containing query preset config information
        :param output_details: A dataclass containing config on how to output results of query
        """

        self._populate_query(
            preset_details=preset_details,
            properties_to_select=output_details.properties_to_select,
        )
        self._query.run(self._cloud_account)
        return self._get_query_output(
            output_details.output_type,
        )

    def _get_query_output(
        self,
        output_type: QueryOutputTypes,
    ) -> QueryReturn:
        """
        method that returns the output of query
        :param output_type: An Enum representing how to output query results
        """
        return {
            QueryOutputTypes.TO_STR: self._query.to_string,
            QueryOutputTypes.TO_HTML: self._query.to_html,
            QueryOutputTypes.TO_LIST: self._query.to_list,
            QueryOutputTypes.TO_OBJECT_LIST: lambda: self._query.to_list(
                as_objects=True
            ),
        }.get(output_type, None)()

    def _populate_query(
        self,
        preset_details: Optional[QueryPresetDetails] = None,
        properties_to_select: Optional[Set[PropEnum]] = None,
    ) -> None:
        """
        method that populates the query before executing.
        :param preset_details: A dataclass containing query preset config information
        :param properties_to_select: A set of properties to get from each result when outputting
        """
        if properties_to_select:
            self._query.select(properties_to_select)
        else:
            self._query.select_all()

        if preset_details:
            self._query.where(
                preset_details.preset, preset_details.prop, preset_details.args
            )
