from typing import Callable
from email_api.email_actions import EmailActions
from structs.smtp_account import SMTPAccount
from st2common.runners.base_action import Action

# pylint: disable=too-few-public-methods


class ST2EmailActions(Action):
    def run(self, submodule: str, smtp_account_name: str, **kwargs):
        """
        Dynamically dispatches to the method wanted in EmailActions (email_api/email_actions.py)
        """
        email_actions = EmailActions()
        func: Callable = getattr(email_actions, submodule)
        return func(
            smtp_account=SMTPAccount.from_pack_config(self.config, smtp_account_name),
            **kwargs
        )
