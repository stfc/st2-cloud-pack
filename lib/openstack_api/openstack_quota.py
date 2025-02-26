from openstack.connection import Connection

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from structs.quota_details import QuotaDetails


# pylint: disable=too-few-public-methods
def set_quota(conn: Connection, details: QuotaDetails):
    """
    Sets quota(s) for a given project. Any 0 values are ignored.
    :param conn: openstack connection object
    :param details: The details of the quota(s) to set
    """
    details.project_identifier = details.project_identifier.strip()
    if not details.project_identifier:
        raise MissingMandatoryParamError("The project name is missing")
    project_id = conn.identity.find_project(
        details.project_identifier, ignore_missing=False
    ).id

    quotas = conn.get_compute_quotas(project_id)

    print(quotas)

    conn.set_compute_quotas(project_id, details)
    _update_quota(conn, project_id, "floating_ips", details.floating_ips)
    _update_quota(conn, project_id, "security_group_rules", details.security_group_rules)
    _update_quota(conn, project_id, "cores", details.cores)
    _update_quota(conn, project_id, "gigabytes", details.gigabytes)
    _update_quota(conn, project_id, "instances", details.instances)
    _update_quota(conn, project_id, "backups", details.backups)
    _update_quota(conn, project_id, "ram", details.ram)
    _update_quota(conn, project_id, "security_groups", details.security_groups)
    _update_quota(conn, project_id, "snapshots", details.snapshots)
    _update_quota(conn, project_id, "volumes", details.volumes)
    


def _update_quota(conn: Connection, project_id: str, quota_id: str, new_val: int):
    """
    Updates a given quota if the quota has a non-zero value
    """
    if new_val == 0:
        return

    kwargs = {"quota": project_id, quota_id: new_val}
    conn.network.update_quota(**kwargs)
