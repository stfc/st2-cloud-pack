from st2reactor.sensor.base import PollingSensor
from jira_api.issue_types.selector import JiraIssue
from jira_api.jira_issue import search_issues
from structs.jira.jira_account import JiraAccount
import jira


class JiraIssueSensor(PollingSensor):
    """
    class to implement an active Sensor to query a JIRA project
    for very specific type of JIRA tickets (issues) and perform
    the corresponding actions via a StackStorm Trigger.

    Active sensors poll a remote service periodically
    (like a cron) instead of waiting for an event input.
    """
    def setup(self):
        """
        set the connection object for our JIRA instance
        """
        endpoint = JiraAccount.atlassian_endpoint
        token = JiraAccount.api_token
        username = JiraAccount.username
        self.jira_client = jira.client.JIRA(  # pylint: disable=attribute-defined-outside-init
            server=endpoint,
            basic_auth=(
                username,
                token,
            ),
        )

    def poll(self):
        """
        check JIRA for new tickets to process
        
        We only search for JIRA tickets in the "TO DO" status.
        This way, once this automation starts working on them and set them
        as "In Progress", they won't be picked up again. 
        """
        # different types of JIRA issues:
        request_type_list = [
            "Request New Project",
            "Add User",
        ]
        for request_type in request_type_list:
            request_type_label = request_type.lower().replace(' ', '_')
            requirements_list = [
                'statusCategory in ("To Do")',
                '"Request Type" = "{request_type}"',
            ]
            issues_list = search_issues(
                JiraAccount,
                'STFCCLOUD',
                requirements_list,
            )
            for issue in issues_list:
                # e.g. "Request New Project" -> "request_new_project"
                st2_jira_issue = JiraIssue(self.jira_client, issue, request_type_label)
                self.process_issue(st2_jira_issue)

    def process_issue(self, issue):
        """
        process an individual JIRA ticket

        :param issue: an individual JIRA ticket
        :type issue: jira.Issue
        """
        trigger_name = f'jira.{issue.request_type}'
        if issue.approved:
            trigger_data = {} # dictionary with data for the rules
            trigger_data['issue_key'] = issue.key
            # we add customer responses from the JIRA Issue's form
            # as part of the data for the trigger
            trigger_data["project_name"] = issue.properties["project_name"]
            trigger_data["users"] = issue.properties["users"]
            trigger_data["cpus"] = issue.properties["cpus"]
            trigger_data["memory"] = issue.properties["memory"]
            trigger_data["shared_storage"] = issue.properties["shared_storage"]
            trigger_data["object_storage"] = issue.properties["object_storage"]
            trigger_data["gpus"] = issue.properties["gpus"]
            trigger_data["contact_email"] = issue.properties["contact_email"]
            self.sensor_service.dispatch(trigger=trigger_name, payload=trigger_data)

    def cleanup(self):
        """
        clean up
        """
        self.jira_client.close()
