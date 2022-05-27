from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from structs.quota_details import QuotaDetails


# pylint: disable=too-few-public-methods
class OpenstackQuota(OpenstackWrapperBase):
    def __init__(self, connection_cls=OpenstackConnection):
        super().__init__(connection_cls)
        self._identity_api = OpenstackIdentity(connection_cls)

    def _update_quota(
        self, cloud_account: str, project_id: str, quota_id: str, new_val: int
    ):
        """
        Updates a given quota if the quota has a non-zero value
        """
        if new_val == 0:
            return

        with self._connection_cls(cloud_account) as conn:
            kwargs = {"project_id": project_id, quota_id: new_val}
            conn.network.update_quota(**kwargs)

    def set_quota(self, cloud_account: str, details: QuotaDetails):
        """
        Sets quota(s) for a given project. Any 0 values are ignored.
        :param cloud_account: The associated credentials to use
        :param details: The details of the quota(s) to set
        """
        project = self._identity_api.find_mandatory_project(
            cloud_account, details.project_identifier
        )
        project_id = project.id

        self._update_quota(
            cloud_account, project_id, "floating_ips", details.num_floating_ips
        )
        self._update_quota(
            cloud_account,
            project_id,
            "security_group_rules",
            details.num_security_group_rules,
        )
