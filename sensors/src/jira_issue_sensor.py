from st2reactor.sensor.base import PollingSensor
from jira_api.jira_issue import search_issues
from structs.jira.jira_account import JiraAccount
import jira

# pylint: disable=attribute-defined-outside-init


class JiraIssueSensor(PollingSensor):
    """
    class to implement an active Sensor to query a JIRA project
    for specific types of JIRA tickets (issues) and perform
    the corresponding actions via a StackStorm Trigger.

    Active sensors poll a remote service periodically
    (like a cron) instead of waiting for an event input.
    """

    def setup(self):
        """
        set the connection object for our JIRA instance
        """

        # At sensor startup, self.config holds the pack’s config
        if not self.config:
            raise ValueError("No config found for sensor")
        jira_account_name = self.config["jira_account_name"]
        self.jira_account = JiraAccount.from_pack_config(self.config, jira_account_name)
        endpoint = self.jira_account.atlassian_endpoint
        token = self.jira_account.api_token
        username = self.jira_account.username
        self.jira_client = jira.client.JIRA(
            server=endpoint,
            basic_auth=(
                username,
                token,
            ),
        )

    def poll(self):
        """
        check JIRA for new tickets to process

        We only search for JIRA tickets in the "Ready For Automation" state.
        This way, once this automation starts working on them and set them
        as "Automation In Progress", they won't be picked up again.
        """
        # different types of JIRA issues:
        request_type_dict = {
            "Request New Project": "jira.request_new_project",
            "Add User": "jira.add_user",
        }
        for request_type, trigger_name in request_type_dict.items():
            requirements_list = [
                'statusCategory in ("Ready For Automation")',
                f'"Request Type" = "{request_type}"',
            ]
            issues_list = search_issues(
                self.jira_account,
                "STFCCLOUD",
                requirements_list,
            )
            for issue in issues_list:
                self.sensor_service.dispatch(
                    trigger=trigger_name, payload={"issue_key": issue.key}
                )

    def cleanup(self):
        """
        clean up
        """
        if self.jira_client:
            self.jira_client.close()
        # Unconditionally drop the resource in-case
        # self.jira_client was not properly instantiated but something
        # tries to use it between now and __exit__
        self.jira_client = None

    def add_trigger(self, trigger):
        """This method is called when trigger is created"""

    def update_trigger(self, trigger):
        """This method is called when trigger is updated"""

    def remove_trigger(self, trigger):
        """This method is called when trigger is deleted"""
