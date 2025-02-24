from openstack.connection import Connection
from openstack_api import openstack_quota
from structs.quota_details import QuotaDetails


def quota_set(
    conn: Connection,
    project_identifier: str,
    num_floating_ips: int,
    num_security_group_rules: int,
    cores: int,
    gigabytes: int,
    key_pairs: int,
    instances: int,
    properties: int,
    ram: int,
    secgroups: int,
    snapshots: int,
    volumes: int,
    volume_type: str,
) -> bool:
    """
    Set a project's quota
    :param conn: Openstack connection object
    :param project_identifier: Name or ID of the Openstack Project
    :param num_floating_ips: The max number of floating IPs (or 0 to skip)
    :param num_security_group_rules: The max number of rules (or 0 to skip)
    :return: status
    """
    openstack_quota.set_quota(
        conn,
        QuotaDetails(project_identifier, num_floating_ips, num_security_group_rules, cores, gigabytes, key_pairs, instances, properties, ram, secgroups, snapshots, volumes, volume_type),
    )
    return True
