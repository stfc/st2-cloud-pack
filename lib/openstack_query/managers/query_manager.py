import logging
from typing import Optional, List, Dict, Any
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

from exceptions.enum_mapping_error import EnumMappingError

logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods


# these search methods map to stackstorm actions which just pass
# user-inputted strings straight here - hence there's a lot of parameters and local variables
# pylint:disable=too-many-arguments
# pylint:disable=too-many-locals
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
        output_details: QueryOutputDetails,
        preset_details: Optional[QueryPresetDetails] = None,
        runner_params: Optional[Dict[str, Any]] = None,
    ) -> QueryReturn:
        """
        method to build the query, execute it, and return the results
        :param output_details: A dataclass containing config on how to output results of query
        :param preset_details: An optional dataclass containing query preset config information
        :param runner_params: An optional set of extra params to pass when calling run()
        """
        logging.info("Running Query")
        if preset_details:
            preset_args = "\n\t".join(
                [f"{key}: '{val}'" for key, val in preset_details.args.items()]
            )
            log_preset_out = f"{preset_details.prop.name} {preset_details.preset.name} with args {preset_args}"
            logging.info("Query Details: %s", log_preset_out)
        else:
            logging.info("Query Details: Getting All")

        if output_details.output_type == QueryOutputTypes.TO_OBJECT_LIST:
            # properties to select will be ignored - hence don't log it
            logging.info(
                "Output Details:\n\t output_type: %s", output_details.output_type.name
            )
        else:
            props_to_select = ",".join(
                [prop.name for prop in output_details.properties_to_select]
            )
            logging.info(
                "Outputting as:\n\t output_type: %s\n\t with properties: %s",
                output_details.output_type.name,
                props_to_select,
            )

        if not runner_params:
            runner_params = {}

        self._populate_output_params(output_details=output_details)

        if preset_details:
            self._query.where(
                preset=preset_details.preset,
                prop=preset_details.prop,
                **preset_details.args,
            )

        self._query.run(self._cloud_account.name, **runner_params)

        return self._get_query_output(
            output_details.output_type,
        )

    def _populate_output_params(self, output_details: QueryOutputDetails):
        """
        method that sets output parameters like group by, sort by and select parameters
        :param output_details: A dataclass containing output parameters to use
        """

        # set select props
        self._query.select(*output_details.properties_to_select)

        # set sort by
        if output_details.sort_by:
            self._query.sort_by(*output_details.sort_by)

        # set group by
        if output_details.group_by:
            self._query.group_by(
                group_by=output_details.group_by,
                group_ranges=output_details.group_ranges,
                include_ungrouped_results=output_details.include_ungrouped_results,
            )

    def _get_query_output(
        self,
        output_type: QueryOutputTypes,
    ) -> QueryReturn:
        """
        method that returns the output of query
        :param output_type: An Enum representing how to output query results
        """
        output_func = {
            QueryOutputTypes.TO_STR: self._query.to_string,
            QueryOutputTypes.TO_HTML: self._query.to_html,
            QueryOutputTypes.TO_LIST: self._query.to_list,
            QueryOutputTypes.TO_OBJECT_LIST: lambda: self._query.to_list(
                as_objects=True
            ),
        }.get(output_type, None)
        if not output_func:
            logging.error(
                "Error: No function mapping found for output type %s "
                "- if you are here as a developer, you must add a mapping in this method"
                "for the enum to a public function in QueryMethods",
                output_type.name,
            )
            raise EnumMappingError(
                f"could not find a mapping for output type {output_type.name}"
            )
        return output_func()

    def search_all(
        self,
        properties_to_select: Optional[List[str]] = None,
        output_type: Optional[str] = None,
        group_by: Optional[str] = None,
        sort_by: Optional[List[str]] = None,
        **kwargs,
    ) -> QueryReturn:
        """
        method that returns a list of all resources
        :param properties_to_select: list of strings representing which properties to select
        :param output_type: string representing how to output the query
        :param group_by: an optional string representing a property to group results by
        :param sort_by: an optional set of tuples representing way which properties to sort results by
        :param kwargs: A set of optional meta params to pass to the query

        """
        logging.info("Running 'search all' query - will output all values")
        output_details = QueryOutputDetails.from_kwargs(
            prop_cls=self._prop_cls,
            properties_to_select=properties_to_select,
            output_type=output_type,
            group_by=group_by,
            sort_by=sort_by,
        )

        return self._build_and_run_query(
            preset_details=None, output_details=output_details, runner_params=kwargs
        )

    def search_by_property(
        self,
        search_mode: str,
        property_to_search_by: str,
        values: List[str],
        properties_to_select: Optional[List[str]] = None,
        output_type: Optional[str] = None,
        group_by: Optional[str] = None,
        sort_by: Optional[List[str]] = None,
        **kwargs,
    ) -> QueryReturn:
        """
        method that builds and runs a query to find generic resource with a selected property
        matching, or not matching given value(s)
        :param search_mode: A string representing a preset Enum ANY_IN or NOT_ANY_IN which dictates what query
        to perform
        if False - use the preset NOT_ANY_IN/NOT_EQUAL_TO
        :param property_to_search_by: A string representing a datetime property Enum that the preset will be used on
        :param values: A list of string values to compare server property against
        :param properties_to_select: list of strings representing which properties to select
        :param output_type: string representing how to output the query
        :param group_by: an optional string representing a property to group results by
        :param sort_by: an optional set of tuples representing way which properties to sort results by
        :param kwargs: A set of optional meta params to pass to the query
        """
        # convert user-given args into enums
        logging.info("Running search by property query")
        logging.debug("converting user-defined property string into enum")
        preset = (
            QueryPresetsString.ANY_IN if search_mode else QueryPresetsString.NOT_ANY_IN
        )
        prop = self._prop_cls.from_string(property_to_search_by)
        args = {"values": values}

        logging.info(
            "This query will find all resources for which %s matches any of [%s]",
            prop.name,
            args["values"],
        )

        # If values contains only one value - use EQUAL_TO/NOT_EQUAL_TO as the preset instead to speed up query
        if len(values) == 1:
            logging.info(
                "query only contains one value - EQUAL_TO preset will be used to speed up query"
            )
            equal_to_preset = {
                QueryPresetsString.ANY_IN: QueryPresetsGeneric.EQUAL_TO,
                QueryPresetsString.NOT_ANY_IN: QueryPresetsGeneric.NOT_EQUAL_TO,
            }.get(preset, None)
            if equal_to_preset:
                preset = equal_to_preset
                args = {"value": values[0]}
        else:
            logging.info("query contains multiple values - ANY_IN preset will be used")

        output_details = QueryOutputDetails.from_kwargs(
            prop_cls=self._prop_cls,
            properties_to_select=properties_to_select,
            output_type=output_type,
            group_by=group_by,
            sort_by=sort_by,
        )

        return self._build_and_run_query(
            preset_details=QueryPresetDetails(
                preset=preset,
                prop=prop,
                args=args,
            ),
            output_details=output_details,
            runner_params=kwargs,
        )

    def search_by_regex(
        self,
        property_to_search_by: str,
        pattern: str,
        properties_to_select: Optional[List[str]] = None,
        output_type: Optional[str] = None,
        group_by: Optional[str] = None,
        sort_by: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        method that builds and runs a query to find generic resource with a property matching regex.
        :param property_to_search_by: A string representing a string property Enum that the preset will be used on
        :param pattern: A string representing a regex pattern
        :param properties_to_select: list of strings representing which properties to select
        :param output_type: string representing how to output the query
        :param group_by: an optional string representing a property to group results by
        :param sort_by: an optional set of tuples representing way which properties to sort results by
        :param kwargs: A set of optional meta params to pass to the query
        """
        logging.info("Running search by property query")

        logging.debug("converting user-defined property string into enum")
        prop = self._prop_cls.from_string(property_to_search_by)

        logging.debug("checking that user-defined regex pattern is valid")
        re.compile(pattern)

        args = {"regex_string": pattern}

        logging.info(
            "This query will find all resources for which %s matches a regex pattern: '%s'",
            prop.name,
            pattern,
        )

        output_details = QueryOutputDetails.from_kwargs(
            prop_cls=self._prop_cls,
            properties_to_select=properties_to_select,
            output_type=output_type,
            group_by=group_by,
            sort_by=sort_by,
        )

        return self._build_and_run_query(
            preset_details=QueryPresetDetails(
                preset=QueryPresetsString.MATCHES_REGEX,
                prop=prop,
                args=args,
            ),
            output_details=output_details,
            runner_params=kwargs,
        )

    def search_by_datetime(
        self,
        search_mode: str,
        property_to_search_by: str,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        properties_to_select: Optional[List[str]] = None,
        output_type: Optional[str] = None,
        group_by: Optional[str] = None,
        sort_by: Optional[List[str]] = None,
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
        :param properties_to_select: list of strings representing which properties to select
        :param output_type: string representing how to output the query
        :param group_by: an optional string representing a property to group results by
        :param sort_by: an optional set of tuples representing way which properties to sort results by
        :param kwargs: A set of optional meta params to pass to the query
        """
        logging.info("Running search by property query")

        logging.debug("converting user-defined property string into enum")
        prop = self._prop_cls.from_string(property_to_search_by)
        preset = QueryPresetsDateTime.from_string(search_mode)
        args = {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": float(seconds),
        }
        logging.info(
            "This query will run a relative datetime query %s %s with args %s",
            prop.name,
            preset.name,
            ",".join(f"{key}: '{val}'" for key, val in args.items()),
        )

        preset_details = QueryPresetDetails(
            preset=preset,
            prop=prop,
            args=args,
        )

        output_details = QueryOutputDetails.from_kwargs(
            prop_cls=self._prop_cls,
            properties_to_select=properties_to_select,
            output_type=output_type,
            group_by=group_by,
            sort_by=sort_by,
        )

        return self._build_and_run_query(
            preset_details=preset_details,
            output_details=output_details,
            runner_params=kwargs,
        )
