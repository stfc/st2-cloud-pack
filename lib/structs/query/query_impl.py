from dataclasses import dataclass

from openstack_query.query_builder import QueryBuilder
from openstack_query.query_output import QueryOutput
from openstack_query.query_parser import QueryParser


@dataclass
class QueryImpl:
    output: QueryOutput
    parser: QueryParser
    builder: QueryBuilder
