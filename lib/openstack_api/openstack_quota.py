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

    # Create dictionary from QuotaDetails object to pass as kwargs
    quotas_dict = dataclasses.asdict(details)
    quotas_dict.pop("project_identifier")

    conn.set_compute_quotas(project_id, **quotas_dict)


def show_quota(conn: Connection, project_id: str):
    conn.get_compute_quotas(project_id)