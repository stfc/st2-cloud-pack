import logging
from datetime import datetime
from typing import List

import requests

from structs.alertmanager.alert_matcher_details import AlertMatcherDetails
from structs.alertmanager.alertmanager_account import AlertManagerAccount
from structs.alertmanager.silence_details import SilenceDetails

logger = logging.getLogger("AlertManagerAPI")


def schedule_silence(
    alertmanager_account: AlertManagerAccount, silence_details: SilenceDetails
) -> str:
    """
    Schedules a silence in alertmanager
        :param alertmanager_account: dataclass for holding alertmanager connection specs
        :type: AlertManagerAccount dataclass object:
        :param silence_details: object with the specs to create a silence
        :type: SilenceDetails dataclass object
        :return: ID of new silence created in Alertmanager
        :rtype: string
        :raises requests.RequestException or requests.HTTPError:
            when the request to the AlertManager failed
    """
    payload = {
        "matchers": silence_details.matchers_raw,
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
    except (requests.HTTPError, requests.RequestException) as req_ex:
        logger.critical(
            "Failed to create silence in Alertmanager: %s\n\tResponse status code: %s\n\tResponse text: %s",
            req_ex,
            req_ex.response.status_code if req_ex.response else "null",
            req_ex.response.text if req_ex.response else "null",
        )
        raise req_ex
    return response.json()["silenceID"]


def remove_silence(alertmanager_account: AlertManagerAccount, silence_id: str) -> None:
    """
    Removes a previously scheduled silence in alertmanager
        :param alertmanager_account: dataclass for holding alertmanager connection specs
        :type alertmanager_account: AlertManagerAccount dataclass object
        :param silence_id: ID of silence to remove
        :type silence_id: string
        :return: None
        :raises requests.RequestException or requests.HTTPError:
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
    except (requests.HTTPError, requests.RequestException) as req_ex:
        logger.critical(
            "Failed to create silence in Alertmanager: %s\n\tResponse status code: %s\n\tResponse text: %s",
            req_ex,
            req_ex.response.status_code if req_ex.response else "null",
            req_ex.response.text if req_ex.response else "null",
        )
        raise req_ex


def remove_silences(
    alertmanager_account: AlertManagerAccount, silence_ids: List[str]
) -> None:
    """
    Removes a list of previously scheduled silences in alertmanager
        :param alertmanager_account: dataclass for holding alertmanager connection specs
        :type alertmanager_account: AlertManagerAccount datclass object
        :param silence_ids: a list of silence ids
        :type silence_ids: List of strings
        :return: None
    """
    for silence_id in silence_ids:
        remove_silence(alertmanager_account, silence_id)


def get_silences(alertmanager_account: AlertManagerAccount) -> dict:
    """
    get all silence events recorded in AlertManager
    :param alertmanager_account: dataclass for holding alertmanager connection specs
    :type alertmanager_account: AlertManagerAccount datclass object
    :return: the dictionary of Silence events currently recorded in AlertManager:
        {
            id: {
                "state":"<active>/<pending>/<expired>,
                "details":SilenceDetails()
            }
        }
    :rtype: dict
    :raises requests.RequestException or requests.HTTPError:
        when the request to the AlertManager failed
    """
    try:
        api_url = f"{alertmanager_account.alertmanager_endpoint}/api/v2/silences"
        response = requests.get(api_url, auth=alertmanager_account.auth, timeout=10)
        response.raise_for_status()
    except (requests.HTTPError, requests.RequestException) as req_ex:
        logger.critical(
            "Failed to create silence in Alertmanager: %s\n\tResponse status code: %s\n\tResponse text: %s",
            req_ex,
            req_ex.response.status_code if req_ex.response else "null",
            req_ex.response.text if req_ex.response else "null",
        )
        raise req_ex

    silences = {}
    for silence in response.json():
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
            matchers=[
                AlertMatcherDetails.from_dict(matcher)
                for matcher in silence["matchers"]
            ],
        )

        # Add to dictionary with ID as key
        silences[silence["id"]] = {
            "details": silence_details,
            "state": silence["status"]["state"],
        }
    return silences


def get_active_silences(alertmanager_account: AlertManagerAccount) -> dict:
    """
    get active silence events, where:
    - the silence has started but has not finished yet
    :param alertmanager_account: dataclass for holding alertmanager connection specs
    :type alertmanager_account: AlertManagerAccount datclass object
    :return: the dictionary of Silence events currently recorded in AlertManager:
        {
            id: {
                "state":"<active>/<pending>/<expired>,
                "details":SilenceDetails()
            }
        }
    :rtype: dict
    """
    return {
        k: v
        for k, v in get_silences(alertmanager_account).items()
        if v["state"] == "active"
    }


def get_valid_silences(alertmanager_account: AlertManagerAccount) -> dict:
    """
    get valid silence events, where:
    - the silence has not started yet
    - the silence has started but has not finished yet
    :param alertmanager_account: dataclass for holding alertmanager connection specs
    :type alertmanager_account: AlertManagerAccount datclass object
    :return: the dictionary of Silence events currently recorded in AlertManager:
        {
            id: {
                "state":"<active>/<pending>/<expired>,
                "details":SilenceDetails()
            }
        }
    :rtype: dict
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
    :param alertmanager_account: dataclass for holding alertmanager connection specs
    :type alertmanager_account: AlertManagerAccount datclass object
    :param hostname: hypervisor hostname to get silences for
    :type hostname: string
    :return: the dictionary of Silence events currently recorded in AlertManager:
        {
            id: {
                "state":"<active>/<pending>/<expired>,
                "details":SilenceDetails()
            }
        }
    :rtype: dict
    """
    hv_silences = {}
    # format of a set of:
    # [("name1", "value1"), ("name2", "value2")] - must match these 2 matchers (logical AND)
    # [("name3", "value3"), ("name4", "value4")] - OR this other set of matchers
    hv_matcher_conditions = [
        [("instance", hostname)],
        [("hostname", hostname)],
    ]

    def check_matchers(matchers: List[AlertMatcherDetails]) -> bool:
        """
        check alert matchers against a set of conditions to see if they are ones pertaining to HVs
        :param matchers: list of AlertMatcherDetails objects
        :type matchers: list
        :return: True - alert matchers are HV related, False - they are not
        :rtype: boolean
        """
        return any(
            all(
                any(
                    matcher.name == name and matcher.value == value
                    for matcher in matchers
                )
                for name, value in condition_set
            )
            for condition_set in hv_matcher_conditions
        )

    for silence_id, silence_values in get_silences(alertmanager_account).items():
        if check_matchers(silence_values["details"].matchers):
            hv_silences[silence_id] = silence_values
    return hv_silences
