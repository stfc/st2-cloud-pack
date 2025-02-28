import dataclasses

from openstack.connection import Connection

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from structs.quota_details import QuotaDetails
from dataclasses import dataclass


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

    # Create dictionaries to pass to each quota call
    compute_quotas = {'cores': details.cores, 'ram': details.ram, 'instances': details.instances}
    network_quotas = {
        'floating_ips': details.floating_ips,
        'security_groups': details.security_groups,
        'security_group_rules': details.security_group_rules,

    }
    volume_quotas = {
        'volumes': details.volumes,
        'snapshots': details.snapshots,
        'gigabytes': details.gigabytes
    }

    conn.set_compute_quotas(project_id, **compute_quotas)
    conn.set_network_quotas(project_id, **network_quotas)
    conn.set_volume_quotas(project_id, **volume_quotas)


def show_quota(conn: Connection, project_id: str):
    conn.get_compute_quotas(project_id)