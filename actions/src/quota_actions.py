from typing import Dict

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

    def quota_show(self, project):
        """
        Show a project's quota
        :param project: ID or Name
        :return: (status (Bool), reason (String))
        """
        # get project id
        project_id = self.find_resource_id(project, self.conn.identity.find_project)
        if not project_id:
            return False, f"Project not found with Name or ID {project}"
        try:
            # quota ID is same as project ID
            quota = self.conn.network.get_quota(quota=project_id, details=True)
        except ResourceNotFound as err:
            return False, f"Quota not found {err}"
        return True, quota
