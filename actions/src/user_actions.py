from typing import Dict, List, Callable

from openstack_action import OpenstackAction
from openstack_api.openstack_query import OpenstackQuery
from openstack_api.openstack_user import OpenstackUser


class UserActions(OpenstackAction):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._user_api: OpenstackUser = config.get(
            "openstack_user_api", OpenstackUser()
        )
        self._query_api: OpenstackQuery = config.get(
            "openstack_query_api", OpenstackQuery()
        )

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    # pylint:disable=too-many-arguments
    def user_list(
        self,
        cloud_account: str,
        query_preset: str,
        properties_to_select: List[str],
        group_by: str,
        get_html: bool,
        **kwargs,
    ) -> str:
        """
        Finds a list of users matching a query
        :param cloud_account: The account from the clouds configuration to use
        :param query_preset: The query to use when searching for images
        :param properties_to_select: The list of properties to select and output from the found images
        :param group_by: Property to group returned results - can be empty for no grouping
        :param get_html: When True tables returned are in html format
        :return: (String or Dictionary of strings) Table(s) of results grouped by the 'group_by' parameter
        """

        images = self._user_api[f"search_{query_preset}"](cloud_account, **kwargs)

        output = self._query_api.parse_and_output_table(
            cloud_account, images, "user", properties_to_select, group_by, get_html
        )

        return output
