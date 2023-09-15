from openstack_query.query_output import QueryOutput
from openstack_query.query_builder import QueryBuilder
from openstack_query.query_parser import QueryParser

from openstack_query.query_methods import QueryMethods
from openstack_query.query_base import QueryBase


# pylint:disable=too-few-public-methods


class QueryWrapper(QueryMethods, QueryBase):
    """
    Wrapper class - This class is a stub class which inherits from QueryMethods and QueryBase and initialises
    them appropriately
    QueryWrapper is a base class for all Query<Resource> subclasses
    """

    def __init__(self):
        self.output = QueryOutput(self.prop_mapping)
        self.parser = QueryParser(self.prop_mapping)
        self.builder = QueryBuilder(
            self.prop_mapping,
            self._get_client_side_handlers().to_list(),
            self._get_server_side_handler(),
        )
        super().__init__(
            builder=self.builder,
            runner=self.query_runner,
            parser=self.parser,
            output=self.output,
        )

        self._query_results = []
