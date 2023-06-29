from typing import Union, List, Any, Optional, Dict
from enum import Enum

from openstack_query.query_output import QueryOutput
from openstack_query.query_builder import QueryBuilder

from openstack_query.handlers.prop_handler import PropHandler
from openstack_query.handlers.presets.preset_handler_base import PresetHandlerBase
from openstack_query.handlers.kwarg_handler import KwargHandler

from exceptions.parse_query_error import ParseQueryError


class QueryWrapper:
    """
    Base class for Query classes. This class exposes all public methods for query api.
    QueryWrapper instantiates QueryBuilder, QueryOutput, and QueryRunner objects and uses them to perform logic
    """

    def __init__(
        self,
        prop_handler: PropHandler,
        preset_handlers: List[PresetHandlerBase],
        kwarg_handler: Optional[KwargHandler] = None,
    ):
        self._query_results = list()

        self.runner = None
        self.output = QueryOutput(prop_handler)
        self.builder = QueryBuilder(
            prop_handler,
            preset_handlers,
            kwarg_handler,
        )

    def select(self, *props: Enum):
        """
        Public method used to 'select' properties that the query will return the value of.
        Mutually exclusive to returning objects using select_all()
        :param props: one or more properties to collect described as enum
        """

        # is an idempotent function
        # an be called multiple times with should aggregate properties to select
        if not props:
            raise ParseQueryError("provide at least one property to select")

        self.output.parse_select(*props, select_all=False)
        return self

    def select_all(self):
        """
        Public method used to 'select' all properties that are available to be returned
        Mutually exclusive to returning objects using select_all()

        Overrides all currently selected properties
        returns list of properties currently selected
        """
        self.output.parse_select(select_all=True)
        return self

    def where(self, preset: Enum, prop: Enum, **kwargs: Optional[Dict[str, Any]]):
        """
        Public method used to set the conditions for the query.
        :param preset: Name of query preset to use
        :param prop: Property that the query preset will be used on
        :param kwargs: a set of optional arguments to pass along with the preset - property pair
            - these kwargs are dependent on the preset given
        """
        self.builder.parse_where(preset, prop, kwargs)
        return self

    def sort_by(self, sort_by: Enum, reverse=False):
        """
        Public method used to configure sorting results
        :param sort_by: name of property to sort by
        :param reverse: False is sort by ascending, True is sort by descending, default False
        """
        raise NotImplementedError

    def group_by(self, group_by: Enum):
        """
        Public method used to configure grouping results.
        :param group_by: name of the property to group by
        """
        raise NotImplementedError

    def run(
        self, cloud_account: str, from_subset: Optional[List[Any]] = None, **kwargs
    ):
        """
        Public method that runs the query provided and outputs
        :param cloud_account: The account from the clouds configuration to use
        :param from_subset: A subset of openstack resources to run query on instead of querying openstacksdk
        :param kwargs: keyword args that can be used to configure details of how query is run
            - valid kwargs specific to resource
        """
        filter_func = self.builder.filter_func()
        filter_kwargs = self.builder.filter_kwargs()

        self._query_results = self.runner.run(
            cloud_account, filter_func, filter_kwargs, from_subset, **kwargs
        )
        self.output.generate_output(self._query_results)

        return self

    def to_list(self, as_objects=False) -> Union[List[Any], List[Dict[str, str]]]:
        """
        Public method to return results as a list
        :param as_objects: whether to return a list of openstack objects, or a list of dictionaries containing selected
        properties
        """
        if as_objects:
            return self._query_results
        return self.output.results()

    def to_string(self, **kwargs) -> str:
        """
        Public method to return results as a table
        :param kwargs: kwargs to pass to generate table
        """
        return self.output.to_string(**kwargs)

    def to_html(self, **kwargs) -> str:
        """
        Public method to return results as html table
        :param kwargs: kwargs to pass to generate table
        """
        return self.output.to_html(**kwargs)
