import json

import requests
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from requests.auth import HTTPBasicAuth
from structs.icinga.downtime_details import DowntimeDetails
from structs.icinga.icinga_account import IcingaAccount


def schedule_downtime(icinga_account: IcingaAccount, details: DowntimeDetails) -> int:
    """
    Schedules a downtime for a host or service

    :param details: Details for scheduling a downtime for a host or service
    :param is_fixed: If true, the downtime is fixed otherwise flexible
    :return: Status code
    """
    basic = HTTPBasicAuth(icinga_account.username, icinga_account.password)

    if not details.object_name:
        raise MissingMandatoryParamError("Missing object name")

    if not details.start_time:
        raise MissingMandatoryParamError("Missing start time")

    if not details.duration:
        raise MissingMandatoryParamError("Missing duration")

    if not details.comment:
        raise MissingMandatoryParamError("Missing comment")

    payload = {
        "type": details.object_type,
        "filter": f'{details.object_type.lower()}.name=="{details.object_name}"',
        "author": "StackStorm",
        "comment": details.comment,
        "start_time": details.start_time,
        "end_time": details.start_time + details.duration,
        "fixed": details.is_fixed,
        "duration": details.duration if not details.is_fixed else None,
    }

    res = requests.post(
        url=f"{icinga_account.icinga_endpoint}/v1/actions/schedule-downtime",
        auth=basic,
        verify=False,
        headers={"Accept": "application/json"},
        data=json.dumps(payload),
        timeout=300,
    )
    return res.status_code


def remove_downtime(
    icinga_account: IcingaAccount, object_type: str, object_name: str
) -> int:
    """
    Removes all downtimes created by stackstorm for a host or service

    :param object_type: Icinga Object type, either Host or Service
    :param object_name: Name of Icinga object
    :return: Status code
    """
    basic = HTTPBasicAuth(icinga_account.username, icinga_account.password)

    if not object_name:
        raise MissingMandatoryParamError("Missing object name")

    payload = {
        "type": object_type,
        "filter": f'{object_type.lower()}.name=="{object_name}"',
        "author": "StackStorm",  # Only remove downtimes created by StackStorm
    }

    res = requests.post(
        url=f"{icinga_account.icinga_endpoint}/v1/actions/remove-downtime",
        auth=basic,
        verify=False,
        headers={"Accept": "application/json"},
        data=json.dumps(payload),
        timeout=300,
    )
    return res.status_code