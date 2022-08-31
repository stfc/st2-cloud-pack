from typing import Dict, Callable

from openstack_action import OpenstackAction
from openstack_api.openstack_network import OpenstackNetwork


class RouterActions(OpenstackAction):
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
    def volume_check(
        self,
        cloud_account: str,
        project_identifier: str,
    ):




