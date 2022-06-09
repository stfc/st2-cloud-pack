from datetime import datetime
from typing import List, Dict

import pytz
import requests
from dateutil import parser
from dateutil.relativedelta import relativedelta

from jupyter_api.api_endpoints import API_ENDPOINTS
from structs.jupyter_last_used import JupyterLastUsed
from st2common.log import getLogger


class UserApi:
    def __init__(self):
        """
        Injects the credentials and threshold from the KV store
        """
        self._log = getLogger(__name__)

    def get_inactive_users(
        self, endpoint: str, auth_token: str, threshold: relativedelta
    ) -> List[JupyterLastUsed]:
        """
        Polls the given endpoint for users and returns the list of users
        """
        self._log.info(f"Polling for inactive users on {endpoint}")
        try:
            users = self.get_users(endpoint, auth_token)
        except RuntimeError as err:
            self._log.warning(f"Failed to get users on {endpoint}: {err}")
            return []

        return self._filter_inactive(users, threshold)

    def get_users(self, endpoint: str, auth_token: str) -> List[JupyterLastUsed]:
        """
        Gets the list of all users from the JupyterHub API
        """
        result = requests.get(
            url=API_ENDPOINTS[endpoint] + "/hub/api/users",
            headers={"Authorization": f"token {auth_token}"},
        )

        if result.status_code == 200:
            return self._pack_users(result.json())
        if result.status_code == 204:
            return []
        raise RuntimeError(f"Failed to get users error was:\n{result.text}")

    def delete_users(self, endpoint: str, auth_token: str, users: List[str]) -> None:
        """
        Removes the given user(s) from the JupyterHub API
        """
        for user in users:
            self._log.info(f"Removing Jupyter user {user}")
            result = requests.delete(
                url=API_ENDPOINTS[endpoint] + f"/hub/api/users/{user}",
                headers={"Authorization": f"token {auth_token}"},
            )

            if result.status_code != 204:
                raise RuntimeError(f"Failed to remove user {user}: {result.text}")

    @staticmethod
    def _pack_users(users: List[Dict]) -> List[JupyterLastUsed]:
        """
        Deserializes the JSON into a bespoke struct for easier processing
        """
        to_return = []
        for user in users:
            last_used = parser.parse(
                user["last_activity"] if user["last_activity"] else user["created"]
            )
            to_return.append((user["name"], last_used))
        return to_return

    def _filter_inactive(
        self, users: List[JupyterLastUsed], threshold: relativedelta
    ) -> List[JupyterLastUsed]:
        """
        Filters inactive users from the list of all users
        """
        return [user for user in users if self._is_inactive(user, threshold)]

    @staticmethod
    def _is_inactive(user: JupyterLastUsed, threshold: relativedelta) -> bool:
        """
        Test if a user is inactive after a given length of time
        """
        # Force UTC timezone
        return user[1] < pytz.utc.localize(datetime.now() - threshold)
