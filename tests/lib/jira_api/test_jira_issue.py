from unittest.mock import MagicMock, patch
import pytest

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from exceptions.jira import MismatchedState, ForbiddenTransition
from jira_api.jira_issue import (
    search_issues,
    create_jira_task,
    add_comment,
    change_state,
)


def test_search_issues_no_requirements():
    """
    Tests search_issues with no additional requirements
    """
    with patch("jira.client.JIRA") as mock_conn:
        mock_account = MagicMock()
        mock_conn = mock_conn.return_value
        mock_conn.search_issues.return_value = ["ISSUE-1", "ISSUE-2"]

        # Call the function
        result = search_issues(mock_account, "TEST_PROJECT")

        # Assertions
        mock_conn.search_issues.assert_called_once_with("project = TEST_PROJECT")
        assert result == ["ISSUE-1", "ISSUE-2"]


def test_search_issues_with_requirements():
    """
    Tests search_issues with multiple requirements
    """
    with patch("jira.client.JIRA") as mock_conn:
        mock_account = MagicMock()
        mock_conn = mock_conn.return_value
        mock_conn.search_issues.return_value = ["ISSUE-3", "ISSUE-4"]

        # Call the function
        result = search_issues(
            mock_account, "TEST_PROJECT", ["status = Open", "assignee = currentUser()"]
        )

        # Assertions
        jql = "project = TEST_PROJECT AND status = Open AND assignee = currentUser()"
        mock_conn.search_issues.assert_called_once_with(jql)
        assert result == ["ISSUE-3", "ISSUE-4"]


def test_search_issues_empty_results():
    """
    Tests search_issues when no issues are found
    """
    with patch("jira.client.JIRA") as mock_conn:
        mock_account = MagicMock()
        mock_conn = mock_conn.return_value
        mock_conn.search_issues.return_value = []

        # Call the function
        result = search_issues(mock_account, "TEST_PROJECT", ["status = Done"])

        # Assertions
        mock_conn.search_issues.assert_called_once_with(
            "project = TEST_PROJECT AND status = Done"
        )
        assert result == []


def test_create_jira_task_project_id_throws():
    """
    Tests exception is raised when missing project id
    """
    mock_issue_details = MagicMock()
    mock_issue_details.project_id = ""
    mock_issue_details.summary = "foo"
    mock_issue_details.description = "bar"

    mock_account = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_jira_task(mock_account, mock_issue_details)


def test_create_jira_task_summary_throws():
    """
    Tests exception is raised when missing summary
    """
    mock_issue_details = MagicMock()
    mock_issue_details.project_id = "foo"
    mock_issue_details.summary = ""
    mock_issue_details.description = "bar"

    mock_account = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_jira_task(mock_account, mock_issue_details)


def test_create_jira_task_description_throws():
    """
    Tests exception is raised when missing description
    """
    mock_issue_details = MagicMock()
    mock_issue_details.project_id = "foo"
    mock_issue_details.summary = "bar"
    mock_issue_details.description = ""

    mock_account = MagicMock()
    with pytest.raises(MissingMandatoryParamError):
        create_jira_task(mock_account, mock_issue_details)


def test_create_jira_task_without_epic_success():
    """
    Tests a task is created without providing an epic
    """
    with patch("jira.client.JIRA") as mock_conn:
        mock_account = MagicMock()

        mock_conn = mock_conn.return_value
        mock_conn.create_issue.return_value = MagicMock(id="123")

        # Create a mock IssueDetails object
        issue_details = MagicMock()
        issue_details.epic_id = None

        # Call the function
        task_id = create_jira_task(mock_account, issue_details)

        # Assertions
        assert task_id == "123"
        mock_conn.create_issue.assert_called_once()


def test_create_jira_task_with_epic_success():
    """
    Tests a task is created when providing an epic
    """
    with patch("jira.client.JIRA") as mock_conn:
        mock_account = MagicMock()

        mock_conn = mock_conn.return_value
        mock_conn.create_issue.return_value = MagicMock(id="123")

        # Create a mock IssueDetails object
        issue_details = MagicMock()

        # Call the function
        task_id = create_jira_task(mock_account, issue_details)

        # Assertions
        assert task_id == "123"
        mock_conn.create_issue.assert_called_once()
        mock_conn.add_issues_to_epic.assert_called_once()


def test_add_comment_calls_jira():
    """
    Tests that add_comment correctly calls the JIRA API
    """
    with patch("jira.client.JIRA") as mock_conn:
        mock_account = MagicMock()

        mock_conn = mock_conn.return_value

        # Call the function
        add_comment(mock_account, "ISSUE-123", "This is a test comment", internal=True)

        # Assertions
        mock_conn.add_comment.assert_called_once_with(
            "ISSUE-123", "This is a test comment", True
        )


def test_add_comment_with_internal_false():
    """
    Tests that add_comment correctly calls the JIRA API with internal=False
    """
    with patch("jira.client.JIRA") as mock_conn:
        mock_account = MagicMock()

        mock_conn = mock_conn.return_value

        # Call the function
        add_comment(mock_account, "ISSUE-123", "Public comment", internal=False)

        # Assertions
        mock_conn.add_comment.assert_called_once_with(
            "ISSUE-123", "Public comment", False
        )


def test_add_comment_empty_text():
    """
    Tests that add_comment raises an error when text is empty
    """
    mock_account = MagicMock()

    with pytest.raises(ValueError):  # Assuming an empty comment should raise an error
        add_comment(mock_account, "ISSUE-123", "")


def test_change_state_success():
    """
    Tests that change_state transitions an issue successfully
    """
    with patch("jira.client.JIRA") as mock_conn:
        mock_account = MagicMock()
        mock_conn = mock_conn.return_value

        mock_issue = MagicMock()
        mock_issue.fields.status.name = "Open"
        mock_conn.issue.return_value = mock_issue
        mock_conn.transitions.return_value = [
            {"id": "21", "to": {"name": "In Progress"}},
            {"id": "31", "to": {"name": "Closed"}},
        ]

        # Call the function
        change_state(mock_account, "ISSUE-123", "In Progress")

        # Assertions
        mock_conn.issue.assert_called_once_with("ISSUE-123")
        mock_conn.transitions.assert_called_once_with("ISSUE-123")
        mock_conn.transition_issue.assert_called_once_with("ISSUE-123", "21")


def test_change_state_invalid_from_state():
    """
    Tests that change_state raises MismatchedState if issue is not in the expected from_state
    """
    with patch("jira.client.JIRA") as mock_conn:
        mock_account = MagicMock()
        mock_conn = mock_conn.return_value

        mock_issue = MagicMock()
        mock_issue.fields.status.name = "To Do"
        mock_conn.issue.return_value = mock_issue

        with pytest.raises(MismatchedState):
            change_state(mock_account, "ISSUE-123", "In Progress", from_state="Open")


def test_change_state_forbidden_transition():
    """
    Tests that change_state raises ForbiddenTransition if no valid transition is found
    """
    with patch("jira.client.JIRA") as mock_conn:
        mock_account = MagicMock()
        mock_conn = mock_conn.return_value

        mock_issue = MagicMock()
        mock_issue.fields.status.name = "Open"
        mock_conn.issue.return_value = mock_issue
        mock_conn.transitions.return_value = [
            {"id": "21", "to": {"name": "Done"}},
            {"id": "31", "to": {"name": "Closed"}},
        ]

        with pytest.raises(ForbiddenTransition):
            change_state(mock_account, "ISSUE-123", "In Progress")
