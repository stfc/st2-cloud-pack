from unittest.mock import MagicMock, patch

from apis.jira_api.structs.jira_issue_details import IssueDetails
from workflows.create_test_issue import create_test_issue


def test_create_test_issue():
    """
    Test creating a test Task in Jira workflow
    """
    mock_jira_account = MagicMock()

    mock_project_id = "JIRA"
    mock_issue_type = "Task"
    mock_summary = "foo"
    mock_description = "bar"
    mock_components = [{"name": "DevOps"}]
    mock_epic_id = "JIRA-01"

    with patch("workflows.create_test_issue.create_jira_task") as mock_create_jira_task:
        create_test_issue(
            jira_account=mock_jira_account,
            project_id=mock_project_id,
            issue_type=mock_issue_type,
            summary=mock_summary,
            description=mock_description,
            components=mock_components,
            epic_id=mock_epic_id,
        )
        mock_create_jira_task.assert_called_once_with(
            account=mock_jira_account,
            issue_details=IssueDetails(
                issue_type="Task",
                project_id="JIRA",
                summary="foo",
                description="bar",
                components=[{"name": "DevOps"}],
                epic_id="JIRA-01",
            ),
        )
