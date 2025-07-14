from openstack.connection import Connection

from meta.exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from apis.openstack_api.structs.quota_details import QuotaDetails


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

    service_methods = {
        "compute": conn.set_compute_quotas,
        "network": conn.set_network_quotas,
        "volume": conn.set_volume_quotas,
    }

    for service_type, service_quotas in details.get_all_quotas().items():
        if service_quotas:
            quota_method = service_methods[service_type]
            quota_method(project_id, **service_quotas)


def show_quota(conn: Connection, project_id: str):
    conn.get_compute_quotas(project_id)
