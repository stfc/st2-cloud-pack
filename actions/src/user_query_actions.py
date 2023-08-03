from typing import Callable
from st2common.runners.base_action import Action
from enums.cloud_domains import CloudDomains
from openstack_query.managers.user_manager import UserManager

# pylint: disable=too-few-public-methods


class UserQueryActions(Action):
    """
    Stackstorm Action class that dynamically dispatches actions related to User Queries to the corresponding
    method in the UserManager class
    Actions that will be handled by this class follow the format user.search.*
    """

    def run(self, submodule: str, cloud_account: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        :param submodule: submodule name which corresponds to method in self
        :param cloud_account: A string representing the cloud domain from the clouds configuration to use
        :param kwargs: All user-defined kwargs to pass to the query
        """

        cloud_account_enum = CloudDomains.from_string(cloud_account)
        user_manager = UserManager(cloud_account=cloud_account_enum)
        query_func: Callable = getattr(user_manager, submodule)
        return query_func(**kwargs)
