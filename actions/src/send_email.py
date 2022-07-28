from typing import Callable, Dict
from email_api.email_api import EmailApi

from st2common.runners.base_action import Action


class SendEmail(Action):
    def __init__(self, *args, config: Dict = None, **kwargs):
        super().__init__(*args, config=config, **kwargs)
        self._api: EmailApi = config.get("email_api", EmailApi())

    def run(self, submodule: str, **kwargs):
        """
        Dynamically dispatches to the method wanted
        """
        func: Callable = getattr(self, submodule)
        return func(**kwargs)

    def send_email(self, **kwargs):
        """
        Sends an email
        :param kwargs: arguments for openstack actions
        :return: (Status (Bool), Output <*>): tuple of action status (succeeded(T)/failed(F)) and the output
        """
        if "body" in kwargs and kwargs["body"]:
            return self._api.send_email(self.config, **kwargs)
        return None
