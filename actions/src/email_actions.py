from typing import Callable
from emailer.email_actions import EmailActions
from structs.smtp_account import SMTPAccount
from st2common.runners.base_action import Action


class ST2EmailActions(Action):
    def run(self, submodule: str, smtp_account_name: str, **kwargs):
        """
        Dynamically dispatches to the method wanted in EmailActions (email_api/email_actions.py)
        """

        func: Callable = getattr(EmailActions, submodule)
        return func(
            smtp_account=SMTPAccount.from_pack_config(self.config, smtp_account_name),
            **kwargs
        )
