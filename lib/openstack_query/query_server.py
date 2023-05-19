from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.query_wrapper import QueryWrapper


class QueryServer(QueryWrapper):
    def __init__(self, connection_cls=OpenstackConnection):
        QueryWrapper.__init__(self, connection_cls)

    @staticmethod
    def _run_query(conn: OpenstackConnection, **kwargs):
        """
        This method runs the query by running openstacksdk commands
        For QueryServer, this command gets all projects available and iteratively finds servers in that project
        :param conn: An OpenstackConnection object
        :param kwargs: a set of extra params to pass into conn.compute.servers
        """
        servers = []
        for project in conn.identity.projects():
            server_filters = {
                "project_id": project['id'],
                "all_tenants": True
            }
            server_filters.update(kwargs)
            servers.extend(list(conn.compute.servers(filters=server_filters)))

        return servers



