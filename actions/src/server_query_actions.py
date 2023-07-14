from typing import Callable, List
from st2common.runners.base_action import Action

from enums.query.props.server_properties import ServerProperties
from enums.query.query_output_types import QueryOutputTypes
from enums.cloud_domains import CloudDomains

from openstack_query.managers.server_manager import ServerManager
from structs.query.query_output_details import QueryOutputDetails


class ServerQueryActions(Action):
    """
    Stackstorm Action class that dynamically dispatches actions related to Server Queries to the corresponding
    method in the ServerManager class
    Actions that will be handled by this class follow the format server.search.*
    """

    def __init__(self, *args, **kwargs):
        self._server_manager = ServerManager(cloud_account=CloudDomains)
        super().__init__(*args, **kwargs)

    def run(
        self,
        submodule: str,
        cloud_account: str,
        properties_to_select: List[str],
        return_type: str = "to_str",
        **kwargs
    ):
        """
        Dynamically dispatches to the ServerManager method wanted
        :param submodule: submodule name which corresponds to function in ServerManager
        :param cloud_account: A string representing the account from the clouds configuration to use
        :param properties_to_select: A list of strings representing the Server Properties to return for each Server query result
        :param return_type: A string representing how to return the results of the query
        :param kwargs: A set of extra parameters to pass to manager method, if any
        """
        server_mgr = self._server_manager(CloudDomains[cloud_account.upper()])
        prop_enums = [ServerProperties[prop.upper()] for prop in properties_to_select]
        return getattr(server_mgr, submodule)(
            output_details=QueryOutputDetails(
                properties_to_select=prop_enums,
                output_type=QueryOutputTypes[return_type.upper()],
            ),
            **kwargs
        )
