from typing import List, Dict, Callable, Any

from openstack.compute.v2.server import Server
from openstack.exceptions import HttpException
from openstack_api.dataclasses import (
    NonExistentCheckParams,
    NonExistentProjectCheckParams,
)

from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.openstack_query_base import OpenstackQueryBase


class OpenstackServer(OpenstackWrapperBase, OpenstackQueryBase):
    def __init__(self, connection_cls=OpenstackConnection):
        OpenstackWrapperBase.__init__(self, connection_cls)
        OpenstackQueryBase.__init__(self, connection_cls)
        self._identity_api = OpenstackIdentity(self._connection_cls)

    def find_non_existent_servers(
        self, cloud_account: str, project_identifier: str
    ) -> Dict[str, List[str]]:
        """
        Returns a dictionary containing the ids of projects along with a list of non-existent servers found within them
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A dictionary containing the non-existent server ids and their projects
        """
        return self._query_api.find_non_existent_objects(
            cloud_account=cloud_account,
            project_identifier=project_identifier,
            check_params=NonExistentCheckParams(
                object_list_func=lambda conn, project: conn.list_servers(
                    detailed=False,
                    all_projects=True,
                    bare=True,
                    filters={
                        "all_tenants": True,
                        "project_id": project.id,
                    },
                ),
                object_get_func=lambda conn, object_id: conn.compute.get_server(
                    object_id
                ),
                object_id_param_name="id",
                object_project_param_name="project_id",
            ),
        )

    def find_non_existent_projects(self, cloud_account: str) -> Dict[str, List[str]]:
        """
        Returns a dictionary containing the ids of non-existent projects along with a list of server ids that
        refer to them
        :param cloud_account: The associated clouds.yaml account
        :return: A dictionary containing the non-existent projects and a list of server ids that refer to them
        """
        return self._query_api.find_non_existent_object_projects(
            cloud_account=cloud_account,
            check_params=NonExistentProjectCheckParams(
                object_list_func=lambda conn: conn.list_servers(
                    detailed=False,
                    all_projects=True,
                    bare=True,
                    filters={
                        "all_tenants": True,
                    },
                ),
                object_id_param_name="id",
                object_project_param_name="project_id",
            ),
        )
