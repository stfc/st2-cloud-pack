from typing import Optional
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from exceptions.jira import MismatchedState, ForbiddenTransition
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


def change_state(
    account: JiraAccount,
    issue_key: str,
    to_state: str,
    from_state: Optional[bool] = None,
):
    """
    If possible, transition a given JIRA Issue to a new state

    :param account: credentials to create a connection with the JIRA server
    :type account: JiraAccount
    :param issue_key: the unique key to identify the Issue to transition
    :type issue_key: str
    :param to_state: the new state we want to transition into
    :type to_state: str
    :param from_state: optional, the current state the Issue is expected to be
    :type from_state: str or None
    :raise MismatchedState: If the argument from_state is being provided,
        but the Issue is not currently in that state,
        we should abort immediately and raise an Exception
    :raise ForbiddenTransition: If the current Issue's workflow does not allow
        a transition from its current state to the new one we want to move into,
        we should raise an Exception
    """
    with JiraConnection(account) as conn:
        issue = conn.issue(issue_key)

        # 1. if needed, double check the current state is the one
        #    passed as [optional] argument from_state
        #    if that is not the case, raise an Exception
        if from_state and issue.fields.status.name != from_state:
            raise MismatchedState(issue_key, from_state)

        # 2. To perform a transition, using method "transition_issue( )"
        #    we have 2 options:
        #    - pass the name of the transition
        #    - pass the id of the transition
        #    it doesn't seem to be possible to just pass the name of the
        #    destination state.
        #    Therefore, we first need to find the transition moving
        #    from current state to the desired one, and use it as argument
        #    to method conn.transition_issue.
        #    If we are not able to find any transition performing that
        #    desired change, we raise an Exception
        allowed_transitions = conn.transitions(issue_key)
        for transition in allowed_transitions:
            if transition["to"]["name"] == to_state:
                conn.transition_issue(issue_key, transition["id"])
                break
        else:
            raise ForbiddenTransition(issue_key, to_state)
