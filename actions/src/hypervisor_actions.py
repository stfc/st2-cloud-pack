from typing import Dict, Callable, List

from openstack.compute.v2.hypervisor import Hypervisor

from openstack_api.dataclasses import QueryParams
from openstack_api.openstack_hypervisor import OpenstackHypervisor
from openstack_api.openstack_query import OpenstackQuery
from st2common.runners.base_action import Action


class HypervisorActions(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, config=config, **kwargs)
        self._hypervisor_api: OpenstackHypervisor = config.get(
            "openstack_hypervisor_api", OpenstackHypervisor()
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
    def hypervisor_list(
        self,
        cloud_account: str,
        query_preset: str,
        properties_to_select: List[str],
        group_by: str,
        get_html: bool,
        **kwargs,
    ) -> List[Hypervisor]:
        """
        Finds all hypervisors matching a particular query
        :param cloud_account: The account from the clouds configuration to use
        :param query_preset: The query to use when searching for hypervisors
        :param properties_to_select: The list of properties to select and output from the found hypervisors
        :param group_by: Property to group returned results - can be empty for no grouping
        :param get_html: When True tables returned are in html format
        :return: (String or Dictionary of strings) Table(s) of results grouped by the 'group_by' parameter
        """

        return self._hypervisor_api.search(
            cloud_account=cloud_account,
            query_params=QueryParams(
                query_preset=query_preset,
                properties_to_select=properties_to_select,
                group_by=group_by,
                get_html=get_html,
            ),
            **kwargs,
        )
