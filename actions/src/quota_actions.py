from typing import Dict, Callable

from openstack.exceptions import ResourceNotFound

from openstack_action import OpenstackAction
from openstack_api.openstack_quota import OpenstackQuota
from structs.quota_details import QuotaDetails


class QuotaActions(OpenstackAction):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, **kwargs)
        self._api: OpenstackQuota = config.get("openstack_api", OpenstackQuota())

        # lists possible functions that could be run as an action
        self.func = {"quota_set": self.quota_set, "quota_show": self.quota_show}

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def quota_set(
        self,
        cloud_account: str,
        project_identifier: str,
        num_floating_ips: int,
        num_security_group_rules: int,
    ) -> bool:
        """
        Set a project's quota
        :param cloud_account: The account from the clouds configuration to use
        :param project_identifier: Name or ID of the Openstack Project
        :param num_floating_ips: The max number of floating IPs (or 0 to skip)
        :param num_security_group_rules: The max number of rules (or 0 to skip)
        :return: status
        """
        self._api.set_quota(
            cloud_account,
            QuotaDetails(
                project_identifier, num_floating_ips, num_security_group_rules
            ),
        )
        return True
