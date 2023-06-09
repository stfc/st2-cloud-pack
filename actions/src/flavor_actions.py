from typing import Dict, Callable, List
from openstack_api.openstack_flavor import OpenstackFlavor
from st2common.runners.base_action import Action


class FlavorActions(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, config=config, **kwargs)
        self._flavor_api: OpenstackFlavor = config.get(
            "openstack_flavor_api", OpenstackFlavor()
        )

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def migrate_missing_flavors(
        self,
        source_cloud: str,
        dest_cloud: str,
    ) -> List[str]:
        """
        Calls missing_flavors from _flavor_api to get a list of flavors that are
        in the source cloud but are missing from the destination cloud and migrates them.
        :param source_cloud: Cloud account for source cloud
        :param dest_cloud: Cloud account for destination cloud
        :returns: List of the names of missing flavors or empty List if no flavors are missing
        """
        return self._flavor_api.migrate_flavors(
            source_cloud=source_cloud,
            dest_cloud=dest_cloud,
        )
