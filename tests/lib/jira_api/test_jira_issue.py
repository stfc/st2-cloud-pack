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


@pytest.fixture(name="mock_jira")
def mock_jira_client():
    with patch("jira.client.JIRA") as mock_conn:
        # we use yield instead of return due the lifecycle of the fixture
        # when a fixture returns a value, the function exits immediately
        # after returning, and pytest has no opportunity to perform cleanup
        # However, when a fixture yields, the test using the fixture runs
        # after the yield statement, and once the test is done,
        # pytest resumes execution of the fixture (after the yield statement),
        # allowing it to clean up resources properly
        yield mock_conn.return_value


@pytest.fixture(name="mock_account")
def mock_jira_account():
    return MagicMock()


@pytest.fixture(name="mock_issue_details")
def mock_jira_issue_details():
    issue = MagicMock()
    issue.project_id = "foo"
    issue.summary = "bar"
    issue.description = "baz"
    issue.epic_id = None  # Default value
    return issue


@pytest.mark.parametrize(
    "requirements, expected_issues, expected_query",
    [
        (None, ["ISSUE-1", "ISSUE-2"], "project = TEST_PROJECT"),
        (
            ["status = Open", "assignee = currentUser()"],
            ["ISSUE-1", "ISSUE-2"],
            "project = TEST_PROJECT AND status = Open AND assignee = currentUser()",
        ),
        (["status = Done"], [], "project = TEST_PROJECT AND status = Done"),
    ],
)
def test_search_issues(
    mock_jira, mock_account, requirements, expected_issues, expected_query
):
    """Tests search_issues with various requirements"""
    mock_jira.search_issues.return_value = expected_issues
    result = search_issues(mock_account, "TEST_PROJECT", requirements)
    mock_jira.search_issues.assert_called_once_with(expected_query)
    assert result == expected_issues


@pytest.mark.parametrize(
    "missing_field",
    ["project_id", "summary", "description"],
)
def test_create_jira_task_missing_fields_throws(
    mock_account, mock_issue_details, missing_field
):
    """Tests exception when missing required fields in create_jira_task"""
    setattr(mock_issue_details, missing_field, "")
    with pytest.raises(MissingMandatoryParamError):
        create_jira_task(mock_account, mock_issue_details)


@pytest.mark.parametrize("epic_id, should_call_epic", [(None, False), ("EPIC-1", True)])
def test_create_jira_task(
    mock_jira, mock_account, mock_issue_details, epic_id, should_call_epic
):
    """Tests task creation with and without an epic"""
    mock_issue_details.epic_id = epic_id
    mock_jira.create_issue.return_value = MagicMock(id="123")

    task_id = create_jira_task(mock_account, mock_issue_details)

    assert task_id == "123"
    mock_jira.create_issue.assert_called_once()
    if should_call_epic:
        mock_jira.add_issues_to_epic.assert_called_once()
    else:
        mock_jira.add_issues_to_epic.assert_not_called()


@pytest.mark.parametrize(
    "comment, is_internal",
    [("This is a test comment", True), ("Public comment", False)],
)
def test_add_comment(mock_jira, mock_account, comment, is_internal):
    """Tests add_comment with different internal flag values"""
    add_comment(mock_account, "ISSUE-123", comment, internal=is_internal)
    mock_jira.add_comment.assert_called_once_with("ISSUE-123", comment, is_internal)


def test_add_comment_empty_text(mock_account):
    """Tests add_comment raises ValueError when text is empty"""
    with pytest.raises(ValueError):
        add_comment(mock_account, "ISSUE-123", "")


@pytest.mark.parametrize(
    "current_state, target_state, transitions, expected_exception",
    [
        (
            "Open",
            "In Progress",
            [
                {"id": "21", "to": {"name": "In Progress"}},
                {"id": "31", "to": {"name": "Closed"}},
            ],
            None,
        ),
        ("To Do", "In Progress", [], MismatchedState),
        (
            "Open",
            "In Progress",
            [
                {"id": "21", "to": {"name": "Done"}},
                {"id": "31", "to": {"name": "Closed"}},
            ],
            ForbiddenTransition,
        ),
    ],
)
def test_change_state(
    mock_jira,
    mock_account,
    current_state,
    target_state,
    transitions,
    expected_exception,
):
    """
    Tests change_state under different conditions

    Parameters:
    - current_state (str): The initial state of the issue before transition.
    - target_state (str): The desired state to transition to.
    - transitions (list[dict]): A list of possible transitions, each represented as
      a dictionary containing an 'id' and a 'to' field specifying the target state.
    - expected_exception (Exception or None): The expected exception if the transition
      is invalid, or None if the transition should succeed.`
    """
    mock_issue = MagicMock()
    mock_issue.fields.status.name = current_state
    mock_jira.issue.return_value = mock_issue
    mock_jira.transitions.return_value = transitions

    if expected_exception:
        with pytest.raises(expected_exception):
            change_state(mock_account, "ISSUE-123", target_state, from_state="Open")
    else:
        change_state(mock_account, "ISSUE-123", target_state)
        mock_jira.issue.assert_called_once_with("ISSUE-123")
        mock_jira.transitions.assert_called_once_with("ISSUE-123")
        mock_jira.transition_issue.assert_called_once_with("ISSUE-123", "21")
