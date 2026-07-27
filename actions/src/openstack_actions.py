from importlib import import_module
from st2common.runners.base_action import Action

from apis.openstack_api.openstack_connection import OpenstackConnection
from apis.alertmanager_api.structs.alertmanager_account import AlertManagerAccount
from apis.email_api.structs.smtp_account import SMTPAccount
from apis.icinga_api.structs.icinga_account import IcingaAccount
from apis.jira_api.structs.jira_account import JiraAccount
from apis.wazuh_api.wazuh import WazuhClient


class OpenstackActions(Action):
    def run(
        self,
        lib_entry_point: str,
        requires_openstack: bool = False,
        requires_wazuh: bool = False,
        **kwargs,
    ):
        """
        Dynamically dispatches to the function wanted
        :param lib_entry_point: path to function that handles action in lib layer
        :param requires_openstack: if action requires connection to openstack
        :param requires_wazuh: if action requires querying the Wazuh server
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

        # in some automations we may need to query the Wazuh server
        # however, we may not need any field in the web form related to Wazuh
        # therefore, it will not be possible to handle the creation of
        # the wazuh client object inside function parse_config()
        # as there is no configuration parameter related to it that can
        # be parsed
        # we trigger the creation of the wazuh client object with an immutable
        # parameter, the same way we do for OpenStack
        if requires_wazuh:
            wazuh = WazuhClient(self.config)
            kwargs["wazuh"] = wazuh

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

        # get token and username from stackstorm config under name jira_account_name
        if "jira_account_name" in kwargs:
            kwargs["jira_account"] = JiraAccount.from_pack_config(
                self.config, kwargs["jira_account_name"]
            )
            del kwargs["jira_account_name"]

        # get password and username from stackstorm config under name icinga_account_name
        if "icinga_account_name" in kwargs:
            kwargs["icinga_account"] = IcingaAccount.from_pack_config(
                self.config, kwargs["icinga_account_name"]
            )
            del kwargs["icinga_account_name"]
        if "alertmanager_account_name" in kwargs:
            kwargs["alertmanager_account"] = AlertManagerAccount.from_pack_config(
                self.config, kwargs["alertmanager_account_name"]
            )
            del kwargs["alertmanager_account_name"]

        if "chatops_reminder_type" in kwargs:
            kwargs["token"] = self.config["chatops_sensor"]["token"]
            kwargs["endpoint"] = self.config["chatops_sensor"]["endpoint"]
            kwargs["channel"] = self.config["chatops_sensor"]["channel"]
            kwargs["reminder_type"] = kwargs["chatops_reminder_type"]
            del kwargs["chatops_reminder_type"]

        return kwargs
