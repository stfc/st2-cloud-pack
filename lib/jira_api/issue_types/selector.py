from jira_api.issue_types import JiraIssueRequestNewProject


def JiraIssue(conn, issue, ticket_type):  # pylint: disable=invalid-name
    """
    function to just select the right class to this type of JIRA issue
    basically, it performs the factory pattern, but with a simple function
    instead of something more obscure like a metaclass

    :param issue: the actual Jira issue we are dealing with
    :type issue: Issue
    :param ticket_type: label to decide which type of JIRA issue it is
    :type ticket_type: str
    :param conn: connection object to interact with JIRA
    :type conn: JiraConnection
    :return: an object of the correponsing JiraIssueXYZ class
    """
    if ticket_type == "Request New Project":
        return JiraIssueRequestNewProject(conn, issue, ticket_type)
    return None
