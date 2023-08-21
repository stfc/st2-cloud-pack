from typing import Callable
from email_api.email_actions import EmailActions
from structs.email.smtp_account import SMTPAccount
from st2common.runners.base_action import Action

# pylint: disable=too-few-public-methods


class ST2EmailActions(Action):
    """
    Stackstorm Action class that dynamically dispatches actions related to sending Emails
    Actions that will be handled by this class follow the format email.*
    Each action will map to one function in class EmailActions located in lib/email_api/email_actions.py
    """

    def run(self, submodule: str, smtp_account_name: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        self.logger.info("Email Action Received - %s", submodule)
        self.logger.debug(
            "with Parameters: %s",
            "\n".join([f"{key}: {val}" for key, val in kwargs.items()]),
        )
        self.logger.info(
            "using SMTP config %s - see config.schema.yaml for details",
            smtp_account_name,
        )

        email_actions = EmailActions()
        func: Callable = getattr(email_actions, submodule)
        self.logger.info("Dispatching function call %s", func)
        smtp_account = SMTPAccount.from_pack_config(self.config, smtp_account_name)
        params = {**{"smtp_account": smtp_account}, **kwargs}
        self.logger.debug("Params: (%s)", params)
        return func(**params)
