import logging
import requests
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from alertmanager_api.silence_details import SilenceDetailsHandler


class AlertManagerAPI:
    """
    class implementing an interface to the Kayobe's alertmanager
    functionalities:
        * create a silence
        * remove an existing silence
    """

    def __init__(self, alertmanager_account):
        """
        :param alertmanager_account: object with credentials
        :type alertmanager_account: AlertManagerAccount
        """
        self.log = logging.getLogger("AlertManagerAPI")
        self.alertmanager_account = alertmanager_account
        self.auth = HTTPBasicAuth(
            alertmanager_account.username, alertmanager_account.password
        )
        self.api_endpoint = alertmanager_account.alertmanager_endpoint

    def schedule_silence(self, silence):
        """
        Schedules a silence in alertmanager

        :param silence: object with the specs to create a silence
        :type silence: SilenceDetails
        :return: a new silence object, including the silence_id
        :rtype: SilenceDetails
        :raises MissingMandatoryParamError:
            if any of the required attributes are missing
            in the silence object:
            instance_name
            start time
            end time
            author
            comment
        :raises requests.exceptions.RequestException:
            when the request to the AlertManager failed
        """
        if not silence.instance_name:
            msg = "Missing silence instance name"
            self.log.critical(msg)
            raise MissingMandatoryParamError(msg)
        if not silence.start_time_dt:
            msg = "Missing silence start time"
            self.log.critical(msg)
            raise MissingMandatoryParamError(msg)
        if not silence.end_time_dt:
            msg = "Missing silence end time"
            self.log.critical(msg)
            raise MissingMandatoryParamError(msg)
        if not silence.author:
            msg = "Missing silence author"
            self.log.critical(msg)
            raise MissingMandatoryParamError(msg)
        if not silence.comment:
            msg = "Missing silence comment"
            self.log.critical(msg)
            raise MissingMandatoryParamError(msg)

        payload = {
            "matchers": [
                {
                    "name": "instance_name",
                    "value": silence.instance_name,
                    "isRegex": False,
                }
            ],
            "startsAt": silence.start_time_str,
            "endsAt": silence.end_time_str,
            "createdBy": silence.author,
            "comment": silence.comment,
        }
        try:
            api_url = f"{self.api_endpoint}/api/v2/silences"
            response = requests.post(
                api_url,
                auth=self.auth,
                headers={"Accept": "application/json"},
                json=payload,
                timeout=10,
            )
            if response.status_code != 200:
                msg = (
                    "Failed to create silence. "
                    f"Response status code: {response.status_code} "
                    f"Response text: {response.text}"
                )
                self.log.error(msg)
                raise RequestException(msg, response=response)
            silence_id = response.json()["silenceID"]
            silence.silence_id = silence_id
            return silence

        except RequestException as req_ex:
            msg = f"Failed to create silence in Alertmanager: {req_ex} "
            if req_ex.response is not None:
                msg += (
                    f"Response status code: {req_ex.response.status_code} "
                    f"Response text: {req_ex.response.text}"
                )
            self.log.critical(msg)
            raise req_ex

    def remove_silence(self, silence):
        """
        Removes a previously scheduled silence in alertmanager

        :param silence: object including the silence_id to be removed
        :type silence: SilenceDetails
        :raises MissingMandatoryParamError: when the silence_id is missing
        :raises requests.exceptions.RequestException:
            when the request to the AlertManager failed
        """
        if not silence.silence_id:
            msg = "Missing silence silence_id"
            self.log.critical(msg)
            raise MissingMandatoryParamError(msg)

        try:
            api_url = f"{self.api_endpoint}/api/v2/silence/{silence.silence_id}"
            response = requests.delete(
                api_url,
                auth=self.auth,
                timeout=10,
            )
            if response.status_code != 200:
                msg = (
                    f"Failed to delete silence with ID {silence.silence_id}. "
                    f"Response status code: {response.status_code} "
                    f"Response text: {response.text}"
                )
                self.log.critical(msg)
                raise RequestException(msg, response=response)
        except RequestException as req_ex:
            msg = f"Failed to delete silence in Alertmanager: {req_ex} "
            if req_ex.response is not None:
                msg += (
                    f"Response status code: {req_ex.response.status_code} "
                    f"Response text: {req_ex.response.text}"
                )
            self.log.critical(msg)
            raise req_ex

    def remove_silences(self, silence_l):
        """
        Removes a list of previously scheduled silences in alertmanager

        :param silence_l: a list of silence instances
        :type silence: SilenceDetailsHandler
        """
        for silence in silence_l:
            self.remove_silence(silence)

    def get_silences(self):
        """
        download all silence events recorded in AlertManager

        :return: the list of Silence events currently recorded in AlertManager
        :rtype: SilenceDetailsHandler
        """
        try:
            api_url = f"{self.api_endpoint}/api/v2/silences"
            response = requests.get(api_url, auth=self.auth, timeout=10)
            silences = response.json()
            handler = SilenceDetailsHandler()
            handler.add_from_json(silences)
            return handler
        except RequestException as req_ex:
            msg = f"Failed to get silences from Alertmanager: {req_ex} "
            if req_ex.response is not None:
                msg += (
                    f"Response status code: {req_ex.response.status_code} "
                    f"Response text: {req_ex.response.text}"
                )
            self.log.critical(msg)
            raise req_ex
