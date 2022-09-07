from datetime import datetime
from typing import List, Dict

import pytz
import requests
from dateutil import parser
from dateutil.relativedelta import relativedelta

from jupyter_api.api_endpoints import API_ENDPOINTS
from structs.jupyter_last_used import JupyterLastUsed
from structs.jupyter_users import JupyterUsers


class UserApi:
    def get_inactive_users(
        self, endpoint: str, auth_token: str, threshold: relativedelta
    ) -> List[JupyterLastUsed]:
        """
        Polls the given endpoint for users and returns the list of users
        """
        try:
            users = self.get_users(endpoint, auth_token)
        except RuntimeError:
            return []

        return self._filter_inactive(users, threshold)

    def get_users(self, endpoint: str, auth_token: str) -> List[JupyterLastUsed]:
        """
        Gets the list of all users from the JupyterHub API
        """
        result = requests.get(
            url=API_ENDPOINTS[endpoint] + "/hub/api/users",
            headers={"Authorization": f"token {auth_token}"},
            timeout=300,
        )

        if result.status_code == 200:
            return self._pack_users(result.json())
        if result.status_code == 204:
            return []
        raise RuntimeError(f"Failed to get users error was:\n{result.text}")

    def delete_users(self, endpoint: str, auth_token: str, users: JupyterUsers) -> None:
        """
        Removes the given user(s) from the JupyterHub API
        """
        user_list = self._get_user_list(users)
        for user in user_list:
            self._delete_single_user(endpoint, auth_token, user)

    def _delete_single_user(self, endpoint: str, auth_token: str, user: str):
        result = requests.delete(
            url=API_ENDPOINTS[endpoint] + f"/hub/api/users/{user}",
            headers={"Authorization": f"token {auth_token}"},
            timeout=300,
        )

        if result.status_code != 204:
            raise RuntimeError(f"Failed to remove user {user}: {result.text}")

    def create_users(self, endpoint: str, auth_token: str, users: JupyterUsers) -> None:
        """
        Creates the given user(s) from the JupyterHub API
        """
        user_list = self._get_user_list(users)
        for user in user_list:
            self._create_single_user(endpoint, auth_token, user)

    def _create_single_user(self, endpoint: str, auth_token: str, user: str):
        result = requests.post(
            url=API_ENDPOINTS[endpoint] + f"/hub/api/users/{user}",
            headers={"Authorization": f"token {auth_token}"},
            timeout=60,
        )

        if result.status_code != 201:
            raise RuntimeError(f"Failed to create user {user}: {result.text}")

    def start_servers(
        self, endpoint: str, auth_token: str, users: JupyterUsers
    ) -> None:
        """
        Starts servers for the given user(s) from the JupyterHub API
        """
        user_list = self._get_user_list(users)
        for user in user_list:
            self._start_single_server(endpoint, auth_token, user)

    def _start_single_server(self, endpoint: str, auth_token: str, user: str):
        result = requests.post(
            url=API_ENDPOINTS[endpoint] + f"/hub/api/users/{user}/server",
            headers={"Authorization": f"token {auth_token}"},
            timeout=60,
        )

        if result.status_code not in (201, 202):
            raise RuntimeError(
                f"Failed to request server for user {user}: {result.text}"
            )

    def stop_servers(self, endpoint: str, auth_token: str, users: JupyterUsers) -> None:
        """
        Stops servers for the given user(s) from the JupyterHub API
        """
        user_list = self._get_user_list(users)
        for user in user_list:
            self._stop_single_server(endpoint, auth_token, user)

    def _stop_single_server(self, endpoint: str, auth_token: str, user: str):
        result = requests.delete(
            url=API_ENDPOINTS[endpoint] + f"/hub/api/users/{user}/server",
            headers={"Authorization": f"token {auth_token}"},
            timeout=60,
        )

        if result.status_code not in (202, 204):
            raise RuntimeError(f"Failed to stop server for user {user}: {result.text}")

    @staticmethod
    def _get_user_list(users: JupyterUsers) -> List[str]:
        """
        Creates list of users from name and indices
        """
        if users.start_index or users.end_index:
            if not (users.start_index and users.end_index):
                raise RuntimeError("Both start_index and end_index must be provided")
            if users.start_index > users.end_index:
                raise RuntimeError("start_index must be less than end_index")

        user_list = (
            [f"{users.name}-{i}" for i in range(users.start_index, users.end_index + 1)]
            if users.start_index
            else [users.name]
        )
        return user_list

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
