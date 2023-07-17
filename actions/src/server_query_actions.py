from typing import Callable
from st2common.runners.base_action import Action
from enums.cloud_domains import CloudDomains
from openstack_query.managers.server_manager import ServerManager

# pylint: disable=too-few-public-methods


class ServerQueryActions(Action):
    """
    Stackstorm Action class that dynamically dispatches actions related to Server Queries to the corresponding
    method in the ServerManager class
    Actions that will be handled by this class follow the format server.search.*
    """

    def run(self, submodule: str, cloud_account: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        :param submodule: submodule name which corresponds to method in self
        :param cloud_account: A string representing the cloud domain from the clouds configuration to use
        :param kwargs: All user-defined kwargs to pass to the query
        """

        cloud_account_enum = CloudDomains.from_string(cloud_account)
        server_manager = ServerManager(cloud_account=cloud_account_enum)
        query_func: Callable = getattr(server_manager, submodule)
        return query_func(**kwargs)
