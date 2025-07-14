from typing import Optional
from apis.jira_api.jira_issue import create_jira_task
from apis.jira_api.structs.jira_issue_details import IssueDetails
from apis.jira_api.structs.jira_account import JiraAccount


# pylint: disable=too-many-arguments
def create_test_issue(
    jira_account: JiraAccount,
    project_id: str,
    issue_type: str,
    summary: str,
    description: str,
    components: str,
    epic_id: Optional[str] = None,
):
    issue_details = IssueDetails(
        project_id=project_id,
        issue_type=issue_type,
        summary=summary,
        description=description,
        components=components,
        epic_id=epic_id,
    )

    create_jira_task(account=jira_account, issue_details=issue_details)
