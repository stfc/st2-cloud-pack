from typing import List
import re
from custom_types.openstack_query.aliases import QueryReturn

from enums.query.query_presets import (
    QueryPresetsDateTime,
    QueryPresetsString,
    QueryPresetsGeneric,
)
from enums.query.props.user_properties import UserProperties
from enums.cloud_domains import CloudDomains

from openstack_query.queries.user_query import UserQuery
from openstack_query.managers.query_manager import QueryManager

from structs.query.query_preset_details import QueryPresetDetails
from structs.query.query_output_details import QueryOutputDetails

from exceptions.parse_query_error import ParseQueryError


class UserManager(QueryManager):
    """
    Manager for querying Openstack user objects.
    """

    def __init__(self, cloud_account: CloudDomains):
        QueryManager.__init__(self, query=UserQuery(), cloud_account=cloud_account)

    def search_all(self, **kwargs) -> QueryReturn:
        """
        method that returns a list of all users
        :param kwargs: A set of optional kwargs to pass to the query
            - properties_to_select - list of strings representing which properties to select
            - output_type - string representing how to output the query
        """
        return self._build_and_run_query(
            preset_details=None,
            output_details=QueryOutputDetails.from_kwargs(prop_cls=UserQuery, **kwargs),
        )

    def search_by_property(
        self, search_mode: str, property_to_search_by: str, values: List[str], **kwargs
    ) -> QueryReturn:
        """
        method that builds and runs a query to find Openstack users with a selected property
        matching, or not matching given value(s)
        :param search_mode: A string representing a preset Enum ANY_IN or NOT_ANY_IN which dictates what query
        to perform
        if False - use the preset NOT_ANY_IN/NOT_EQUAL_TO
        :param property_to_search_by: A string representing a datetime property Enum that the preset will be used on
        :param values: A list of string values to compare user property against
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
                prop=UserProperties.from_string(property_to_search_by),
                args=args,
            ),
            output_details=QueryOutputDetails.from_kwargs(prop_cls=UserQuery, **kwargs),
        )

    def search_by_regex(self, property_to_search_by: str, pattern: str, **kwargs):
        """
        method that builds and runs a query to find Openstack users with a selected property matching regex.
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
                prop=UserProperties.from_string(property_to_search_by),
                args=args,
            ),
            output_details=QueryOutputDetails.from_kwargs(
                prop_cls=UserProperties, **kwargs
            ),
        )

    def search_by_datetime(
        self, search_mode: str, property_to_search_by: str, **kwargs
    ):
        """
        Method to search by datetime.
        For querying users this will raise an error as this is not possible
        """
        raise ParseQueryError("Cannot query by datatime with users")
