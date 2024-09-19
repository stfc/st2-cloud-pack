from unittest.mock import MagicMock, patch
import pytest

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from jira_api.jira_issue import create_jira_task, JiraConnection


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


def test_jira_connection():
    """
    Tests a client to connect to a atlassian server is created and closed
    """
    with patch("jira.client.JIRA") as mock_jira:
        mock_account = MagicMock()
        mock_account.atlassian_endpoint = "https://example.atlassian.net/"
        mock_account.username = "foo"
        mock_account.api_token = "bar"

        # Use the JiraConnection class in a with statement
        with JiraConnection(mock_account) as conn:
            # Check if the JIRA instance was created with the correct parameters
            mock_jira.assert_called_once_with(
                server="https://example.atlassian.net/", basic_auth=("foo", "bar")
            )
            # Check if the connection object is the mock JIRA instance
            assert conn == mock_jira.return_value


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
