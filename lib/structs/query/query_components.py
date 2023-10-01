from dataclasses import dataclass

from openstack_query.query_blocks.query_builder import QueryBuilder
from openstack_query.query_blocks.query_output import QueryOutput
from openstack_query.query_blocks.query_parser import QueryParser
from openstack_query.query_blocks.query_executer import QueryExecuter


@dataclass
class QueryComponents:
    output: QueryOutput
    parser: QueryParser
    builder: QueryBuilder
    executer: QueryExecuter
