from openstack_query.mappings import MappingInterface
from openstack_query.query_builder import QueryBuilder
from openstack_query.query_output import QueryOutput
from openstack_query.query_parser import QueryParser
from structs.query.query_impl import QueryImpl


class QueryFactory:
    @staticmethod
    def build_query_deps(mapping_cls: MappingInterface) -> QueryImpl:
        prop_mapping = mapping_cls.get_prop_mapping()

        output = QueryOutput(prop_mapping)
        parser = QueryParser(prop_mapping)
        builder = QueryBuilder(
            mapping_cls.get_prop_mapping(),
            mapping_cls.get_client_side_handlers(),
            mapping_cls.get_server_side_handler(),
        )
        return QueryImpl(output, parser, builder)
