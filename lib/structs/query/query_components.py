from dataclasses import dataclass

from openstack_query.query_blocks.query_builder import QueryBuilder
from openstack_query.query_blocks.query_output import QueryOutput
from openstack_query.query_blocks.query_parser import QueryParser
from openstack_query.query_blocks.query_executer import QueryExecuter


@dataclass
class QueryComponents:
    """
    A dataclass to hold configured objects that together make up parts of the query
    :param output: holds a configured QueryOutput object which is used to output the results of the query
        - and handles the select(), to_string(), to_html(), etc commands
    :param parser: holds a configured QueryParser object which is used to handle sort_by/group_by commands
    :param builder: holds a configured QueryBuilder object which is used to handler where() commands
    :param executer: holds a configured QueryExecute object which is used to execute the query
        - handles the run() command
    """

    output: QueryOutput
    parser: QueryParser
    builder: QueryBuilder
    executer: QueryExecuter
