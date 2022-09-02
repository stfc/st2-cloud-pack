from typing import Dict, Callable, Optional

from jupyter_api.user_api import UserApi
from jupyter_api.jupyter_helpers import JupyterHelpers
from st2common.runners.base_action import Action
from structs.jupyter_users import JupyterUsers


class Jupyter(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, config=config, **kwargs)
        self._api: UserApi = config.get("user_api", UserApi())
        self._jupyter_helpers: JupyterHelpers = config.get(
            "jupyter_helpers", JupyterHelpers()
        )

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def user_delete(
        self,
        jupyter_env: str,
        user: str,
        first_index: Optional[int] = None,
        last_index: Optional[int] = None,
    ):
        """
        Delete users from the given environment
        """
        jupyter_keys = self.config["jupyter"]
        token = self._jupyter_helpers.get_token(jupyter_env, jupyter_keys)
        user_details = JupyterUsers(user, first_index, last_index)
        self._api.delete_users(jupyter_env, token, user_details)

    def user_create(
        self,
        jupyter_env: str,
        user: str,
        first_index: Optional[int] = None,
        last_index: Optional[int] = None,
    ):
        """
        Create users from the given environment
        """
        jupyter_keys = self.config["jupyter"]
        token = self._jupyter_helpers.get_token(jupyter_env, jupyter_keys)
        user_details = JupyterUsers(user, first_index, last_index)
        self._api.create_users(jupyter_env, token, user_details)

    def server_start(
        self,
        jupyter_env: str,
        user: str,
        first_index: Optional[int] = None,
        last_index: Optional[int] = None,
    ):
        """
        Start servers for users from the given environment
        """
        jupyter_keys = self.config["jupyter"]
        token = self._jupyter_helpers.get_token(jupyter_env, jupyter_keys)
        user_details = JupyterUsers(user, first_index, last_index)
        self._api.start_servers(jupyter_env, token, user_details)

    def server_stop(
        self,
        jupyter_env: str,
        user: str,
        first_index: Optional[int] = None,
        last_index: Optional[int] = None,
    ):
        """
        Stop servers for users from the given environment
        """
        jupyter_keys = self.config["jupyter"]
        token = self._jupyter_helpers.get_token(jupyter_env, jupyter_keys)
        user_details = JupyterUsers(user, first_index, last_index)
        self._api.stop_servers(jupyter_env, token, user_details)
