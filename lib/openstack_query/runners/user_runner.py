from typing import Optional, Dict, List

from openstack.identity.v3.user import User
from openstack.exceptions import ResourceNotFound

from openstack_api.openstack_connection import OpenstackConnection
from openstack_query.runners.query_runner import QueryRunner

from exceptions.parse_query_error import ParseQueryError

# pylint:disable=too-few-public-methods


class UserRunner(QueryRunner):
    """
    Runner class for openstack Server resource.
    ServerRunner encapsulates running any openstacksdk Server commands
    """
    STFC_DOMAIN_ID = "TEST"
    
    def _run_query(
        self,
        conn: OpenstackConnection,
        filter_kwargs: Optional[Dict[str, str]] = None,
        
    ) -> List[User]:
        """
        This method runs the query by running openstacksdk commands

        For ServerQuery, this command gets all projects available and iteratively finds servers that belong to that
        project
        :param conn: An OpenstackConnection object - used to connect to openstacksdk
        :param filter_kwargs: An Optional set of filter kwargs to pass to conn.compute.servers()
            to limit the servers being returned. - see https://docs.openstack.org/api-ref/compute/#list-servers
        :param from_projects: takes a list of openstack projects to run the query on

        """
        if not filter_kwargs:
            filter_kwargs = {} 
        if "domain_id" not in filter_kwargs.keys():
            filter_kwargs.update({"domain_id" : self.STFC_DOMAIN_ID})
        conn.identity.users(**filter_kwargs)

 
