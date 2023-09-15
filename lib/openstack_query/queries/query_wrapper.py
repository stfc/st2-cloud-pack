from enums.query.props.prop_enum import PropEnum
from openstack_query.query_output import QueryOutput
from openstack_query.query_builder import QueryBuilder
from openstack_query.query_parser import QueryParser

from openstack_query.query_methods import QueryMethods
from openstack_query.query_base import QueryBase
from openstack_query.runners.query_runner import QueryRunner


# pylint:disable=too-few-public-methods


class QueryWrapper(QueryMethods, QueryBase):
    """
    Wrapper class - This class is a stub class which inherits from QueryMethods and QueryBase and initialises
    them appropriately
    QueryWrapper is a base class for all Query<Resource> subclasses
    """

    def __init__(self, query_runner: QueryRunner, prop_enum_cls: PropEnum):
        self.runner = query_runner
        self.output = QueryOutput(prop_enum_cls)
        self.parser = QueryParser(prop_enum_cls)
        self.builder = QueryBuilder(
            prop_enum_cls,
            self._get_client_side_handlers().to_list(),
            self._get_server_side_handler(),
        )
        super().__init__(
            builder=self.builder,
            runner=self.runner,
            parser=self.parser,
            output=self.output,
        )

        self._query_results = []
