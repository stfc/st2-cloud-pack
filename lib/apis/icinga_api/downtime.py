import json
import requests
from meta.exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from requests.auth import HTTPBasicAuth
from apis.icinga_api.enums.icinga_objects import IcingaObject
from apis.icinga_api.structs.downtime_details import DowntimeDetails
from apis.icinga_api.structs.icinga_account import IcingaAccount


def schedule_downtime(icinga_account: IcingaAccount, details: DowntimeDetails) -> None:
    """
    Schedules a downtime for a host or service

    :param details: Details for scheduling a downtime for a host or service
    :param is_fixed: If true, the downtime is fixed otherwise flexible
    """
    basic = HTTPBasicAuth(icinga_account.username, icinga_account.password)

    if not details.object_name:
        raise MissingMandatoryParamError("Missing object name")

    if not details.start_time:
        raise MissingMandatoryParamError("Missing start time")

    if not details.end_time:
        raise MissingMandatoryParamError("Missing end time")

    if not details.comment:
        raise MissingMandatoryParamError("Missing comment")

    payload = {
        "type": details.object_type.name.capitalize(),
        "filter": f'{details.object_type.name.lower()}.name=="{details.object_name}"',
        "author": "StackStorm",
        "comment": details.comment,
        "start_time": details.start_time,
        "end_time": details.end_time,
        "fixed": details.is_fixed,
        "duration": details.duration if not details.is_fixed else None,
        "all_services": details.object_type == IcingaObject.HOST,
    }

    res = requests.post(
        url=f"{icinga_account.icinga_endpoint}/v1/actions/schedule-downtime",
        auth=basic,
        verify="/var/lib/icinga2/certs/ca.crt",
        headers={"Accept": "application/json"},
        data=json.dumps(payload),
        timeout=300,
    )

    res.raise_for_status()  # Raises HTTPError, if one occurred


def remove_downtime(
    icinga_account: IcingaAccount, object_type: IcingaObject, object_name: str
) -> None:
    """
    Removes all downtimes created by stackstorm for a host or service

    :param object_type: Icinga Object type, either Host or Service
    :param object_name: Name of Icinga object
    """
    basic = HTTPBasicAuth(icinga_account.username, icinga_account.password)

    if not object_name:
        raise MissingMandatoryParamError("Missing object name")

    payload = {
        "type": object_type.name.capitalize(),
        "filter": f'{object_type.name.lower()}.name=="{object_name}"',
        "author": "StackStorm",  # Only remove downtimes created by StackStorm
    }

    res = requests.post(
        url=f"{icinga_account.icinga_endpoint}/v1/actions/remove-downtime",
        auth=basic,
        verify="/var/lib/icinga2/certs/ca.crt",
        headers={"Accept": "application/json"},
        data=json.dumps(payload),
        timeout=300,
    )

    res.raise_for_status()  # Raises HTTPError, if one occurred
