from structs.jira.jira_account import JiraAccount

from jira_api.connection import JiraConnection
from jira_api.jira_issue import change_state, add_comment
from jira_api.issue_types.new_project_request import NewProjectRequestIssue
from workflows.create_project import create_project
from openstack.connection import Connection

def request_new_project(
        jira_account: JiraAccount,
        issue_key,
###        project_name: str,
###        users,
###        cpus,
###        memory,
###        shared_storage,
###        object_storage,
###        gpus,
###        contact_email,
    ):
    """
    Implement the workflow to create a new Project in OpenStack
    1. set JIRA ticket as "In Progress"
    2. create the new Project in OpenStack
    3. reply to the JIRA ticket
    """
    try:
        jira = NewProjectRequestIssue(jira_account, issue_key)
        user_data = jira.properties
        change_state(jira_account, issue_key, "Automation In Progress")
        out = create_project(**user_data)
        add_comment(jira_account, issue_key, out)
        change_state(jira_account, issue_key, "Waiting for Review")
    except Exception as ex:
        raise ex
