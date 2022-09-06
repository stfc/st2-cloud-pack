from typing import Dict, Callable

from openstack_action import OpenstackAction
from openstack_api.openstack_network import OpenstackNetwork


class volume_management(OpenstackAction):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._api: OpenstackNetwork = config.get("openstack_api", OpenstackNetwork())

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    # pylint: disable=too-many-arguments
    def get_disk_space(
        self,
        cloud_account: str,
        project_identifier: str,
        query_preset: str,
    ):
        """
        Retrieves volume list
        :param: cloud_account (String): Cloud account to use
        :param: project_identifier (String): project id
        """

        volumes = self._server_api[f"search_{query_preset}"](
            cloud_account, project_identifier
        )
        return volumes
















