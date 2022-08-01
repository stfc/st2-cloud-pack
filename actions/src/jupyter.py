from typing import Dict, Callable, List

from jupyter_api.user_api import UserApi
from st2common.runners.base_action import Action


class Jupyter(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, config=config, **kwargs)
        self._api: UserApi = config.get("user_api", UserApi())

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def user_delete(self, jupyter_env: str, users: List[str]):
        """
        Delete users from the given environment
        """
        jupyter_keys = self.config["jupyter"]

        key_name = None
        env = jupyter_env.casefold()
        if env == "prod".casefold():
            key_name = "prod_token"
        if env == "training".casefold():
            key_name = "training_token"
        if env == "dev".casefold():
            key_name = "dev_token"
        if not key_name:
            raise KeyError("Unknown Jupyter environment")

        token = jupyter_keys[key_name]
        self._api.delete_users(jupyter_env, token, users)
