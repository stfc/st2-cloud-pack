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
        env = jupyter_env.casefold()
        key_name = None
        if env == "prod".casefold():
            key_name = "jupyter.prod_token"
        if env == "training".casefold():
            key_name = "jupyter.training_token"
        if env == "dev".casefold():
            key_name = "jupyter.dev_token"

        if not key_name:
            raise KeyError("Unknown Jupyter environment")

        token = self.action_service.get_value(key_name, local=False, decrypt=True)
        self._api.delete_users(jupyter_env, token, users)
