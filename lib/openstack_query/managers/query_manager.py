from typing import Optional, Set, List
import re

from enums.query.query_output_types import QueryOutputTypes
from enums.query.props.prop_enum import PropEnum
from enums.cloud_domains import CloudDomains
from enums.query.query_presets import (
    QueryPresetsString,
    QueryPresetsGeneric,
    QueryPresetsDateTime,
)

from structs.query.query_output_details import QueryOutputDetails
from structs.query.query_preset_details import QueryPresetDetails

from openstack_query.queries.query_wrapper import QueryWrapper
from custom_types.openstack_query.aliases import QueryReturn

# pylint:disable=too-few-public-methods


class QueryManager:
    """
    This class is the base class for all managers.
    Managers hold a query object and several methods which build and run specific queries
    """

    def __init__(
        self, query: QueryWrapper, cloud_account: CloudDomains, prop_cls: PropEnum
    ):
        self._query = query
        self._cloud_account = cloud_account
        self._prop_cls = prop_cls

    def _build_and_run_query(
        self,
        preset_details: QueryPresetDetails,
        output_details: QueryOutputDetails,
    ) -> QueryReturn:
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
            self._query.select(*properties_to_select)
        else:
            self._query.select_all()

        if preset_details:
            self._query.where(
                preset=preset_details.preset,
                prop=preset_details.prop,
                **preset_details.args,
            )

    def search_all(self, **kwargs) -> QueryReturn:
        """
        method that returns a list of all resources
        :param kwargs: A set of optional kwargs to pass to the query
            - properties_to_select - list of strings representing which properties to select
            - output_type - string representing how to output the query
        """
        return self._build_and_run_query(
            preset_details=None,
            output_details=QueryOutputDetails.from_kwargs(
                prop_cls=self._prop_cls, **kwargs
            ),
        )

    def search_by_property(
        self, search_mode: str, property_to_search_by: str, values: List[str], **kwargs
    ) -> QueryReturn:
        """
        method that builds and runs a query to find generic resource with a selected property
        matching, or not matching given value(s)
        :param search_mode: A string representing a preset Enum ANY_IN or NOT_ANY_IN which dictates what query
        to perform
        if False - use the preset NOT_ANY_IN/NOT_EQUAL_TO
        :param property_to_search_by: A string representing a datetime property Enum that the preset will be used on
        :param values: A list of string values to compare server property against
        :param kwargs: A set of optional kwargs to pass to the query
            - properties_to_select - list of strings representing which properties to select
            - output_type - string representing how to output the query
        """
        args = {"values": values}
        preset = (
            QueryPresetsString.ANY_IN if search_mode else QueryPresetsString.NOT_ANY_IN
        )

        # If values contains only one value - use EQUAL_TO/NOT_EQUAL_TO as the preset instead to speed up query
        if len(values) == 1:
            equal_to_preset = {
                QueryPresetsString.ANY_IN: QueryPresetsGeneric.EQUAL_TO,
                QueryPresetsString.NOT_ANY_IN: QueryPresetsGeneric.NOT_EQUAL_TO,
            }.get(preset, None)
            if equal_to_preset:
                preset = equal_to_preset
                args = {"value": values[0]}

        return self._build_and_run_query(
            preset_details=QueryPresetDetails(
                preset=preset,
                prop=self._prop_cls.from_string(property_to_search_by),
                args=args,
            ),
            output_details=QueryOutputDetails.from_kwargs(
                prop_cls=self._prop_cls, **kwargs
            ),
        )

    def search_by_regex(self, property_to_search_by: str, pattern: str, **kwargs):
        """
        method that builds and runs a query to find generic resource with a property matching regex.
        :param property_to_search_by: A string representing a string property Enum that the preset will be used on
        :param pattern: A string representing a regex pattern
        :param kwargs: A set of optional kwargs to pass to the query
            - properties_to_select - list of strings representing which properties to select
            - output_type - string representing how to output the query
        """

        re.compile(pattern)
        args = {"regex_string": pattern}

        return self._build_and_run_query(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsString.MATCHES_REGEX,
                prop=self._prop_cls.from_string(property_to_search_by),
                args=args,
            ),
            output_details=QueryOutputDetails.from_kwargs(
                prop_cls=self._prop_cls, **kwargs
            ),
        )

    # maybe convert days, hours, minutes, seconds into a dataclass?
    # pylint:disable=too-many-arguments
    def search_by_datetime(
        self,
        search_mode: str,
        property_to_search_by: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        **kwargs,
    ) -> QueryReturn:
        """
        method that builds and runs a datetime-related query on Generic Resource, and then returns results.
        Uses UTC timezone
        :param search_mode: A string representing what type of datetime query will be run - set as a Datetime Preset
        that the query will use
        :param property_to_search_by: A string representing a datetime property Enum that the preset will be used on
        - must be datetime compatible
        :param days: (Optional) Number of relative days in the past from now to use as threshold
        :param hours: (Optional) Number of relative hours in the past from now to use as threshold
        :param minutes: (Optional) Number of relative minutes in the past from now to use as threshold
        :param seconds: (Optional) Number of relative seconds in the past from now to use as threshold
        :param kwargs: A set of optional kwargs to pass to the query
            - properties_to_select - list of strings representing which properties to select
            - output_type - string representing how to output the query
        """
        preset_details = QueryPresetDetails(
            preset=QueryPresetsDateTime.from_string(search_mode),
            prop=self._prop_cls.from_string(property_to_search_by),
            args={
                "days": days,
                "hours": hours,
                "minutes": minutes,
                "seconds": float(seconds),
            },
        )

        return self._build_and_run_query(
            preset_details=preset_details,
            output_details=QueryOutputDetails.from_kwargs(
                prop_cls=self._prop_cls, **kwargs
            ),
        )
