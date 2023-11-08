from st2common.runners.base_action import Action

from structs.email.smtp_account import SMTPAccount


class WorkflowActions(Action):
    def run(self, submodule_name: str, action_name: str, **kwargs):
        """
        Dynamically dispatches to the function wanted
        :param submodule_name: submodule name which corresponds to module in workflow
        :param action_name: name of file/function which corresponds to function that will handle the action
        :param kwargs: all user-defined kwargs to pass to the function
        """
        workflow = __import__(f"workflows.{submodule_name}.{action_name}")
        submodule = getattr(workflow, f"{submodule_name}")
        action_module = getattr(submodule, action_name)
        action_func = getattr(action_module, action_name)

        self.logger.info(
            "Workflow Action Received - %s/%s", submodule_name, action_name
        )
        self.logger.debug(
            "with Parameters: %s",
            "\n".join([f"{key}: {val}" for key, val in kwargs.items()]),
        )

        kwargs = self.parse_configs(**kwargs)
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
        return kwargs
