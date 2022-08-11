from typing import Dict, Callable

from free_ipa.password import generate_password
from st2common.runners.base_action import Action


class FreeIpa(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, config=config, **kwargs)
        self._password_gen: Callable = config.get("password_gen", generate_password)

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def generate_password(self, password_length: int) -> str:
        return self._password_gen(password_length)
