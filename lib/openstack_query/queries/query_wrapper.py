from openstack_query.query_executer import QueryExecuter
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
        self._query_results = []
        self.executer = QueryExecuter(
            self.prop_enum_cls,
            self.runner_cls,
        )
        self.output = QueryOutput(self.prop_enum_cls)
        self.parser = QueryParser(self.prop_enum_cls)
        self.builder = QueryBuilder(
            self.prop_enum_cls,
            self._get_client_side_handlers().to_list(),
            self._get_server_side_handler(),
        )
