from typing import Optional
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from structs.jira.jira_account import JiraAccount
from structs.jira.jira_issue_details import IssueDetails
from jira_api.connection import JiraConnection


def create_jira_task(account, issue_details: IssueDetails) -> str:
    """
    Creates a JIRA issue in a given project
    :param project_id: ID or key of the JIRA project
    :return: Jira Issue ID
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


def add_comment(
    account: JiraAccount, issue_key: str, text: str, internal: Optional[bool] = True
):
    """
    Add a comment to an existing JIRA Issue.

    :param account: credentials to create a connection with the JIRA server
    :type account: JiraAccount
    :param issue_key: the unique key to identify the Issue to update
    :type issue_key: str
    :param text: the content of the comment being added to the JIRA issue
    :type text: str
    :param internal: boolean to decide if the comment is internal or a reply to the user
    :type internal: bool
    """
    if not text:
        raise ValueError("Comment text cannot be empty")
    with JiraConnection(account) as conn:
        conn.add_comment(issue_key, text, internal)
