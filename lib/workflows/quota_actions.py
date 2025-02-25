from openstack.connection import Connection
from openstack_api import openstack_quota
from structs.quota_details import QuotaDetails


def quota_set(
    conn: Connection,
    project_identifier: str,
    floating_ips: int,
    secgroup_rules: int,
    cores: int,
    gigabytes: int,
    instances: int,
    backups: int,
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
        QuotaDetails(project_identifier, 
                     floating_ips, 
                     secgroup_rules, 
                     cores, 
                     gigabytes,
                     instances, 
                     backups, 
                     ram, 
                     secgroups, 
                     snapshots, 
                     volumes),
    )
    return True
