import time
import logging
from typing import Union, List, Any, Optional, Dict, Tuple

from enums.query.props.prop_enum import PropEnum
from enums.query.query_presets import QueryPresets
from enums.cloud_domains import CloudDomains

from openstack_query.query_output import QueryOutput
from openstack_query.query_builder import QueryBuilder
from openstack_query.query_parser import QueryParser
from openstack_query.runners.server_runner import QueryRunner

from exceptions.parse_query_error import ParseQueryError
from custom_types.openstack_query.aliases import OpenstackResourceObj, PropValue

logger = logging.getLogger(__name__)


class QueryMethods:
    """
    Interface for Query Classes. This class exposes all public methods for query api.
    """

    def __init__(
        self,
        builder: QueryBuilder,
        runner: QueryRunner,
        parser: QueryParser,
        output: QueryOutput,
    ):
        self.builder = builder
        self.runner = runner
        self.parser = parser
        self.output = output
        self._query_results = None
        self._query_results_as_objects = None

    def select(self, *props: PropEnum):
        """
        Public method used to 'select' properties that the query will return the value of.
        Mutually exclusive to returning objects using select_all()
        :param props: one or more properties to collect described as enum
        """

        # is an idempotent function
        # an be called multiple times with should aggregate properties to select
        logger.debug("select() called, with props: %s", [prop.name for prop in props])
        if not props:
            raise ParseQueryError("provide at least one property to select")

        self.output.parse_select(*props, select_all=False)
        logger.debug(
            "selected props are now: %s",
            [prop.name for prop in self.output.selected_props],
        )
        return self

    def select_all(self):
        """
        Public method used to 'select' all properties that are available to be returned
        Mutually exclusive to returning objects using select_all()

        Overrides all currently selected properties
        returns list of properties currently selected
        """
        logger.debug("select_all() called - getting all properties")
        self.output.parse_select(select_all=True)
        logger.debug(
            "selected props are now: %s",
            [prop.name for prop in self.output.selected_props],
        )
        return self

    def where(
        self, preset: QueryPresets, prop: PropEnum, **kwargs: Optional[Dict[str, Any]]
    ):
        """
        Public method used to set the conditions for the query.
        :param preset: QueryPreset Enum to use
        :param prop: Property Enum that the query preset will be used on
        :param kwargs: a set of optional arguments to pass along with the preset - property pair
            - these kwargs are dependent on the preset given
        """
        kwargs_log_str = "<none>"
        if kwargs:
            kwargs_log_str = "\n\t\t".join(
                [f"{key}: '{arg}'" for key, arg in kwargs.items()]
            )

        logger.debug(
            "where() called, with args:"
            "\n\t preset: %s"
            "\n\t prop: %s"
            "\n\t preset-args:\n\t\t%s",
            preset.name,
            prop.name,
            kwargs_log_str,
        )

        self.builder.parse_where(preset, prop, kwargs)
        return self

    def sort_by(self, *sort_by: Tuple[PropEnum, bool]):
        """
        Public method used to configure sorting results
        :param sort_by: Tuple of property enum to sort by and boolean representing sorting order
            - False (ascending) or True (descending)
        """
        self.parser.parse_sort_by(*sort_by)

    def group_by(
        self,
        group_by: PropEnum,
        group_ranges: Optional[Dict[str, List[PropValue]]] = None,
        include_ungrouped_results: bool = False,
    ):
        """
        Public method used to configure how to group results.
        :param group_by: name of the property to group by
        :param group_ranges: a set of optional group mappings - group name to list of values of
        selected group by property to be included in each group
        :param include_ungrouped_results: an optional flag to include a "ungrouped" group to the
        output of values found that were
        not specified in group mappings - ignored if group ranges not given
        """
        if self.parser.group_by_prop:
            raise ParseQueryError("group by already set")

        self.parser.parse_group_by(group_by, group_ranges, include_ungrouped_results)

    def run(
        self,
        cloud_account: CloudDomains,
        from_subset: Optional[List[OpenstackResourceObj]] = None,
        **kwargs,
    ):
        """
        Public method that runs the query provided and outputs
        :param cloud_account: An Enum for the account from the clouds configuration to use
        :param from_subset: A subset of openstack resources to run query on instead of querying openstacksdk
        :param kwargs: keyword args that can be used to configure details of how query is run
            - valid kwargs specific to resource
        """

        local_filters = self.builder.client_side_filter
        server_filters = self.builder.server_side_filters

        meta_param_log_str = "<none>"
        if kwargs:
            from_params_dict = {"from_subset": len(from_subset)} if from_subset else {}
            log_kwargs = {**kwargs, **from_params_dict}
            meta_param_log_str = ", ".join(
                [f"{key}: '{val}'" for key, val in log_kwargs.items()]
            )

        logger.debug(
            "run called "
            "\n\t with server_side_filters: '%s'"
            "\n\t with client_side_filters: '%s'"
            "\n\t with run meta args: '%s'",
            "<none>" if not server_filters else server_filters,
            "<none>" if not local_filters else local_filters,
            meta_param_log_str,
        )

        logger.debug("run started")
        start = time.time()
        results = self.runner.run(
            cloud_account, local_filters, server_filters, from_subset, **kwargs
        )
        logger.debug("run completed - time elapsed: %s seconds", time.time() - start)

        parsed_results = self.parser.run_parser(results)
        # if parsed results are grouped results
        if isinstance(parsed_results, dict):
            self._query_results = {}
            self._query_results_as_objects = {}
            for name, group in parsed_results.items():
                self._query_results.update({name: self.output.generate_output(group)})
                self._query_results_as_objects.update({name: group})

        # if parsed results aren't grouped
        else:
            self._query_results = self.output.generate_output(parsed_results)
            self._query_results_as_objects = parsed_results
        return self

    def to_list(self, as_objects=False) -> Union[List[Any], List[Dict[str, str]]]:
        """
        Public method to return results as a list/dict
        :param as_objects: if true return result as openstack objects,
        else return result as dictionaries containing selected properties
        """
        if as_objects:
            return self._query_results_as_objects
        return self._query_results

    def to_string(self, title: Optional[str] = None, **kwargs) -> str:
        """
        Public method to return results as table(s)
        :param title: an optional title for the table(s)
        :param kwargs: kwargs to pass to generate table
        """
        return self.output.to_string(self._query_results, title, **kwargs)

    def to_html(self, title: Optional[str] = None, **kwargs) -> str:
        """
        Public method to return results as html table
        :param title: an optional title for the table(s) - will be converted to html automatically
        :param kwargs: kwargs to pass to generate table
        """
        return self.output.to_html(self._query_results, title, **kwargs)
