from openstack.connection import Connection
from openstack_api import openstack_quota
from structs.quota_details import QuotaDetails


def quota_set(
    conn: Connection,
    project_identifier: str,
    floating_ips: int,
    security_group_rules: int,
    cores: int,
    gigabytes: int,
    instances: int,
    backups: int,
    ram: int,
    security_groups: int,
    snapshots: int,
    volumes: int,
) -> bool:
    """
    Set a project's quota
    :param conn: Openstack connection object
    :param project_identifier: Name or ID of the Openstack Project
    :param floating_ips: The max number of floating IPs (or 0 to skip)
    :param security_group_rules: The max number of rules (or 0 to skip)
    :param cores: The max number of cores (or 0 to skip)
    :param gigabytes: The max number of gigabytes (or 0 to skip)
    :param instances: The max number of instances (or 0 to skip)
    :param backups: The max number of backups (or 0 to skip)
    :param ram: The max amount of ram in MB (or 0 to skip)
    :param security_groups: The max number of security groups (or 0 to skip)
    :param snapshots: The max number of snapshots (or 0 to skip)
    :param volumes: The max number of volumes (or 0 to skip)
    :return: status
    """
    openstack_quota.set_quota(
        conn,
        QuotaDetails(
            project_identifier,
            floating_ips,
            security_group_rules,
            cores,
            gigabytes,
            instances,
            backups,
            ram,
            security_groups,
            snapshots,
            volumes,
        ),
    )
    return True
