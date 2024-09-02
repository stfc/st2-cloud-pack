from typing import Dict, Callable

from st2common.runners.base_action import Action

from openstack_api.openstack_hypervisor import OpenstackHypervisor


class HypervisorActions(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, config=config, **kwargs)
        self._api: OpenstackHypervisor = config.get(
            "openstack_api", OpenstackHypervisor()
        )

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def find_hypervisor(self, cloud_account: str, search_type: str):
        """
        Runs a search for hypervisors based on the search type
        """
        return self._api.find_hypervisor(cloud_account, search_type)
