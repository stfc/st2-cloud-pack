from typing import Dict, Callable, List

from free_ipa.freeipa_helpers import FreeIpaHelpers
from free_ipa.password import generate_password
from st2common.runners.base_action import Action


class FreeIpa(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        """constructor class"""
        super().__init__(*args, config=config, **kwargs)
        self._freeipa_helpers: FreeIpaHelpers = config.get(
            "freeipa_helpers", FreeIpaHelpers()
        )
        self._password_gen: Callable = config.get("password_gen", generate_password)

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def generate_users(
        self, user_base_name: str, user_start_index: int, user_end_index: int
    ) -> List[str]:
        return self._freeipa_helpers.generate_users(
            user_base_name, user_start_index, user_end_index
        )

    def generate_password(self, password_length: int) -> str:
        return self._password_gen(password_length)
