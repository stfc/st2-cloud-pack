import jira
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from structs.jira.jira_account import JiraAccount
from structs.jira.jira_issue_details import IssueDetails


class JiraConnection:
    """
    Wrapper for Jira connection
    """

    def __init__(self, account: JiraAccount):
        self.conn = None
        self.endpoint = account.atlassian_endpoint
        self.token = account.api_token
        self.username = account.username

    def __enter__(self):
        self.conn = jira.client.JIRA(
            server=self.endpoint,
            basic_auth=(
                self.username,
                self.token,
            ),
        )
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


def create_jira_task(account, issue_details: IssueDetails) -> str:
    """
    Creates a JIRA issue in a given project
    :param project_id: ID or key of the JIRA project
    """
    if not issue_details.project_id:
        raise MissingMandatoryParamError("The project id is missing")
    if not issue_details.summary:
        raise MissingMandatoryParamError("The issue summary is missing")
    if not issue_details.description:
        raise MissingMandatoryParamError("The issue description is missing")
    fields = {
        "project": issue_details.project_id,
        "issuetype": issue_details.issue_type.capitalize(),  # Task, Bug, Epic,...
        "summary": issue_details.summary,
        "description": issue_details.description,
        "components": issue_details.components,
    }

    with JiraConnection(account) as conn:
        # Check jira project exists
        conn.project(issue_details.project_id)
        task = conn.create_issue(fields=fields)

        if not issue_details.epic_id:
            return task.id

        # Check jira epic exists
        conn.issue(issue_details.epic_id)

        conn.add_issues_to_epic(epic_id=issue_details.epic_id, issue_keys=task.key)
        return task.id
