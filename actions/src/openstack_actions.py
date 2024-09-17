from importlib import import_module
from structs.jira.jira_account import JiraAccount
from st2common.runners.base_action import Action

from openstack_api.openstack_connection import OpenstackConnection
from structs.email.smtp_account import SMTPAccount


class OpenstackActions(Action):
    def run(self, lib_entry_point: str, requires_openstack: bool = False, **kwargs):
        """
        Dynamically dispatches to the function wanted
        :param lib_entry_point: path to function that handles action in lib layer
        :param requires_openstack: if action requires connection to openstack
        :param kwargs: all user-defined kwargs to pass to the function
        """
        module, fn_name = lib_entry_point.rsplit(".", 1)
        action_module = import_module(module)
        action_func = getattr(action_module, fn_name)

        self.logger.info("Action Received - %s", lib_entry_point)
        self.logger.debug(
            "with Parameters: %s",
            "\n".join([f"{key}: {val}" for key, val in kwargs.items()]),
        )

        kwargs = self.parse_configs(**kwargs)
        if not requires_openstack:
            return action_func(**kwargs)

        # setup openstack connection
        with OpenstackConnection(kwargs["cloud_account"]) as conn:
            kwargs["conn"] = conn
            del kwargs["cloud_account"]
            return action_func(**kwargs)

    def parse_configs(self, **kwargs):
        """
        parse user-defined kwargs and get back stackstorm config info
        """
        if "smtp_account_name" in kwargs:
            kwargs["smtp_account"] = SMTPAccount.from_pack_config(
                self.config, kwargs["smtp_account_name"]
            )
            del kwargs["smtp_account_name"]
        if "atlassian_account_name" in kwargs:
            kwargs["atlassian_account"] = JiraAccount.from_pack_config(
                self.config, kwargs["atlassian_account_name"]
            )
            del kwargs["atlassian_account_name"]
        return kwargs
