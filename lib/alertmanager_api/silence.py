import logging
import requests
import json
from datetime import datetime

from typing import List, Dict
from structs.alertmanager.alertmanager_account import AlertManagerAccount
from structs.alertmanager.silence_details import SilenceDetails

logger = logging.getLogger("AlertManagerAPI")


def schedule_silence(
    alertmanager_account: AlertManagerAccount, silence_details: SilenceDetails
) -> str:
    """
    Schedules a silence in alertmanager
        :param alertmanager_account: dataclass for holding alertmanager connection specs
        :param silence_details: object with the specs to create a silence
        :return: ID of new silence created in Alertmanager
        :raises requests.exceptions.RequestException:
            when the request to the AlertManager failed
    """
    payload = {
        "matchers": silence_details.matchers,
        "startsAt": silence_details.start_time_str,
        "endsAt": silence_details.end_time_str,
        "createdBy": silence_details.author,
        "comment": silence_details.comment,
    }
    api_url = f"{alertmanager_account.alertmanager_endpoint}/api/v2/silences"
    try:
        response = requests.post(
            api_url,
            auth=alertmanager_account.auth,
            headers={"Accept": "application/json"},
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
    except requests.HTTPError as req_ex:
        logger.critical(
            f"Failed to create silence in Alertmanager: {req_ex}"
            f"Response status code: {req_ex.response.status_code if req_ex.response else 'null'} "
            f"Response text: {req_ex.response.text if req_ex.response else 'null'}"
        )
        raise req_ex
    return response.json()["silenceID"]


def remove_silence(alertmanager_account: AlertManagerAccount, silence_id: str) -> None:
    """
    Removes a previously scheduled silence in alertmanager
        :param alertmanager_account: dataclass for holding alertmanager connection specs
        :param silence_id: ID of silence to remove
        :raises requests.exceptions.RequestException:
            when the request to the AlertManager failed
    """
    api_url = (
        f"{alertmanager_account.alertmanager_endpoint}/api/v2/silence/{silence_id}"
    )
    try:
        response = requests.delete(
            api_url,
            auth=alertmanager_account.auth,
            timeout=10,
        )
        response.raise_for_status()
    except requests.HTTPError as req_ex:
        logger.critical(
            f"Failed to create silence in Alertmanager: {req_ex}"
            f"Response status code: {req_ex.response.status_code if req_ex.response else 'null'} "
            f"Response text: {req_ex.response.text if req_ex.response else 'null'}"
        )
        raise req_ex


def remove_silences(
    alertmanager_account: AlertManagerAccount, silence_ids: List[str]
) -> None:
    """
    Removes a list of previously scheduled silences in alertmanager
        :param alertmanager_account: dataclass for holding alertmanager connection specs
        :param silence_ids: a list of silence ids
        :type silence_ids: List of strings
    """
    for id in silence_ids:
        remove_silence(alertmanager_account, id)


def get_silences(alertmanager_account: AlertManagerAccount) -> Dict:
    """
    get all silence events recorded in AlertManager
    :param alertmanager_account: dataclass for holding alertmanager connection specs
    :return: the dictionary of Silence events currently recorded in AlertManager:
        {
            id: {
                "state":"<active>/<pending>/<expired>,
                "details":SilenceDetails()
            }
        }
    """
    try:
        api_url = f"{alertmanager_account.alertmanager_endpoint}/api/v2/silences"
        response = requests.get(api_url, auth=alertmanager_account.auth, timeout=10)
        response.raise_for_status()
    except requests.HTTPError as req_ex:
        logger.critical(
            f"Failed to create silence in Alertmanager: {req_ex}"
            f"Response status code: {req_ex.response.status_code if req_ex.response else 'null'} "
            f"Response text: {req_ex.response.text if req_ex.response else 'null'}"
        )
        raise req_ex

    silences = {}
    for silence in json.loads(response.json()):
        # Create SilenceDetails instance
        silence_details = SilenceDetails(
            # Convert ISO format strings to datetime objects
            start_time_dt=datetime.fromisoformat(
                silence["startsAt"].replace("Z", "+00:00")
            ),
            end_time_dt=datetime.fromisoformat(
                silence["endsAt"].replace("Z", "+00:00")
            ),
            author=silence["createdBy"],
            comment=silence["comment"],
            matchers=silence["matchers"],
        )

        # Add to dictionary with ID as key
        silences[silence["id"]] = {
            "details": silence_details,
            "state": silence["status"]["state"],
        }
    return silences


def get_active_silences(alertmanager_account: AlertManagerAccount):
    """
    get active silence events, where:
    - the silence has started but has not finished yet
    :param alertmanager_account: dataclass for holding alertmanager connection specs
    :return: the dictionary of Silence events currently recorded in AlertManager:
        {
            id: {
                "state":"<active>/<pending>/<expired>,
                "details":SilenceDetails()
            }
        }
    """
    return {
        k: v
        for k, v in get_silences(alertmanager_account).items()
        if v["state"] == "active"
    }


def get_valid_silences(alertmanager_account: AlertManagerAccount):
    """
    get valid silence events, where:
    - the silence has not started yet
    - the silence has started but has not finished yet
    :param alertmanager_account: dataclass for holding alertmanager connection specs
    :return: the dictionary of Silence events currently recorded in AlertManager:
        {
            id: {
                "state":"<active>/<pending>/<expired>,
                "details":SilenceDetails()
            }
        }
    """
    return {
        k: v
        for k, v in get_silences(alertmanager_account).items()
        if v["state"] in ["active", "pending"]
    }


def get_hv_silences(alertmanager_account: AlertManagerAccount, hostname: str):
    """
    get silences pertaining to a hv, where:
    - the silence has a "matcher" where the "name" is "instance" and the "value" matches the given hostname
    :param hostname: hypervisor hostname to get silences for
    :param alertmanager_account: dataclass for holding alertmanager connection specs
    :return: the dictionary of Silence events currently recorded in AlertManager:
        {
            id: {
                "state":"<active>/<pending>/<expired>,
                "details":SilenceDetails()
            }
        }
    """
    hv_silences = {}
    for silence_id, silence_details in get_silences(alertmanager_account).items():
        for matcher in silence_details["details"].matchers:
            if matcher["name"] == "instance" and matcher["value"] == hostname:
                hv_silences[silence_id] = silence_details
    return hv_silences
