from openstack.connection import Connection
from apis.openstack_api import openstack_quota
from apis.openstack_api.structs.quota_details import QuotaDetails


def quota_set(
    conn: Connection,
    project_identifier: str,
    floating_ips: int,
    security_group_rules: int,
    cpu_cores: int,
    cinder_storage: int,
    ram: int,
    instances: int,
    backups: int,
    security_groups: int,
    snapshots: int,
    volumes: int,
) -> bool:
    """
    Set a project's quota
    :param conn: Openstack connection object
    :param project_identifier: Name or ID of the Openstack Project
    :param floating_ips: The max number of floating IPs (or blank to skip)
    :param security_group_rules: The max number of rules (or blank to skip)
    :param cpu_cores: The max number of cores (or blank to skip)
    :param cinder_storage: The max amount of Cinder storage, in GB (or blank to skip)
    :param ram: The max amount of ram, in MB (or blank to skip)
    :param instances: The max number of instances (or blank to skip)
    :param backups: The max number of backups (or blank to skip)
    :param security_groups: The max number of security groups (or blank to skip)
    :param snapshots: The max number of snapshots (or blank to skip)
    :param volumes: The max number of volumes (or blank to skip)
    :return: status
    """
    openstack_quota.set_quota(
        conn,
        QuotaDetails(
            project_identifier,
            floating_ips,
            security_group_rules,
            cpu_cores,
            cinder_storage,
            ram,
            instances,
            backups,
            security_groups,
            snapshots,
            volumes,
        ),
    )
    return True
