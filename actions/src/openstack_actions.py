from importlib import import_module

from st2common.runners.base_action import Action

from apis.openstack_api.openstack_connection import OpenstackConnection
from apis.alertmanager_api.structs.alertmanager_account import AlertManagerAccount
from apis.email_api.structs.smtp_account import SMTPAccount
from apis.icinga_api.structs.icinga_account import IcingaAccount
from apis.jira_api.structs.jira_account import JiraAccount

ACCOUNT_CONFIGS = {
    "smtp_account_name": ("smtp_account", SMTPAccount),
    "jira_account_name": ("jira_account", JiraAccount),
    "icinga_account_name": ("icinga_account", IcingaAccount),
    "alertmanager_account_name": ("alertmanager_account", AlertManagerAccount),
}


class OpenstackActions(Action):
    def run(
        self, lib_entry_point: str, create_openstack_connection: bool = False, **kwargs
    ):
        """
        Dynamically dispatches to the function wanted
        :param lib_entry_point: path to function that handles action in lib layer
        :param create_openstack_connection: if action requires opening a connection openstack before running it
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

        # the query library accepts only "cloud_account" at the moment,
        # so we need to passthrough "cloud_account" without creating a connection object
        # TODO: modify the query library to accept both a conn object and cloud_account str
        # so we can pass conn instead of cloud_account and remove the need for
        # flag "create_openstack_connection"
        if "cloud_account" not in kwargs or not create_openstack_connection:
            return action_func(**kwargs)

        # this is a helper that will create a conn object before running the action
        # saves from having to do it in the workflows/ layer
        # At the moment we open a connection object for all actions because all our actions
        # involve running openstack commands.
        # TODO: revisit this mechanism as we add more actions that don't interact with openstack
        with OpenstackConnection(kwargs["cloud_account"]) as conn:
            kwargs["conn"] = conn
            del kwargs["cloud_account"]
            return action_func(**kwargs)

    def parse_configs(self, **kwargs):
        """
        parse user-defined kwargs and get back stackstorm config info
        """

        # setup structs to load in credentials from st2 pack config
        for name_key, (obj_key, loader) in ACCOUNT_CONFIGS.items():
            if name_key in kwargs:
                kwargs[obj_key] = loader.from_pack_config(
                    self.config, kwargs.pop(name_key)
                )

        # TODO: convert this into ChatOpsAccount struct
        if "chatops_reminder_type" in kwargs:
            kwargs["token"] = self.config["chatops_sensor"]["token"]
            kwargs["endpoint"] = self.config["chatops_sensor"]["endpoint"]
            kwargs["channel"] = self.config["chatops_sensor"]["channel"]
            kwargs["reminder_type"] = kwargs["chatops_reminder_type"]
            del kwargs["chatops_reminder_type"]

        return kwargs
