from typing import Optional, List
from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from exceptions.jira import MismatchedState, ForbiddenTransition
from structs.jira.jira_account import JiraAccount
from structs.jira.jira_issue_details import IssueDetails
from jira_api.connection import JiraConnection


def search_issues(
    account: JiraAccount,
    project_name: str,
    requirements_list: Optional[List[str]] = None,
):
    """
    Search the list of Issues in a given project that meet
    all requirements.

    :param account: credentials to create a connection with the JIRA server
    :type account: JiraAccount
    :param project_name: name of the JIRA project
    :type project_name: str
    :param requirements: potential constraints for the query. For example
        the status of the issues or the value of some field
    :type requirements: list

    :return: the list of found Issues
    :rtype: list

    :Example:
        .. code-block:: python
            search_issues(
                account,
                "PROJECT_1",
                [
                    "statusCategory in ('To Do', 'In Progress')",
                ]
            )
            search_issues(
                account,
                "PROJECT_2",
                [
                    "statusCategory in ('To Do')",
                    "assignee = currentUser()",
                ]
            )
            search_issues(
                account,
                "PROJECT_3",
                [
                    "statusCategory in ('To Do', 'In Progress')",
                    "'Request Type' = 'New Project'",
                ]
            )
    """
    jql = f"project = {project_name}"
    if requirements_list is not None:
        for req in requirements_list:
            jql += " AND " + req
    with JiraConnection(account) as conn:
        return conn.search_issues(jql)


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
    transition_name: Optional[str] = None,
    to_state: Optional[str] = None,
    from_state: Optional[str] = None,
):
    """
    If possible, transition a given JIRA Issue to a new state.

    :param account: Credentials to create a connection with the JIRA server
    :type account: JiraAccount
    :param issue_key: The unique key identifying the Issue to transition
    :type issue_key: str
    :param transition_name: (Optional) the name of the transition to apply
    :type transition_name: str or None
    :param to_state: (Optional) the name of the new state we want to transition into
    :type to_state: str or None
    :param from_state: (Optional) the current state the Issue is expected to be in
    :type from_state: str or None
    :raise ValueError: If both transition_name and to_state are provided, or if neither is provided
    :raise MismatchedState: If from_state is provided but the Issue is not currently in that state
    :raise ForbiddenTransition: If the desired transition or state is not found in the Issue's workflow
    """
    # 1. Check that exactly one among "transition_name" or "to_state" is provided
    if (transition_name is None and to_state is None) or (transition_name and to_state):
        raise ValueError("You must specify exactly one of transition_name or to_state.")

    # 2. Connect to JIRA
    with JiraConnection(account) as conn:
        # 3. Retrieve the Issue object for the given key
        issue = conn.issue(issue_key)

        # 4. If a from_state is provided, make sure the Issue is currently in that state
        if from_state and issue.fields.status.name != from_state:
            raise MismatchedState(issue_key, from_state)

        # 5. Get the list of possible transitions
        allowed_transitions = conn.transitions(issue_key)

        # 6. If a transition name is provided, find a matching transition by "name"
        if transition_name:
            for transition in allowed_transitions:
                # If we find a matching name, perform the transition and return
                if transition["name"] == transition_name:
                    conn.transition_issue(issue_key, transition["id"])
                    break
            else:
                # If no matching transition was found, raise ForbiddenTransition
                raise ForbiddenTransition(
                    issue_key, f"transition_name={transition_name}"
                )

        # 7. Otherwise, if a to_state is provided, find a matching transition by "to" state name
        else:
            for transition in allowed_transitions:
                # If we find the transition whose "to" state matches, perform the transition and return
                if transition["to"]["name"] == to_state:
                    conn.transition_issue(issue_key, transition["id"])
                    break
            else:
                # If no matching state transition was found, raise ForbiddenTransition
                raise ForbiddenTransition(issue_key, to_state)
