from unittest.mock import MagicMock, patch
import pytest
from sensors.src.jira_issue_sensor import JiraIssueSensor


@pytest.fixture(name="sensor")
def jira_sensor_fixture():
    """
    Pytest fixture that initializes an instance of JiraIssueSensor.

    What is a fixture?
    -------------------
    - A fixture is a reusable setup function that pytest runs before executing a test function.
    - It provides a fresh instance of an object for each test to prevent test interference.
    - This fixture returns a fully initialized JiraIssueSensor instance.

    What does this fixture do?
    --------------------------
    - Creates a `sensor_service` mock (simulates StackStorm's event handling system).
    - Sets up a fake configuration dictionary (`config`) to simulate actual configuration values.
    - Returns a `JiraIssueSensor` instance with the mock `sensor_service` and sample configuration.
    """

    # Create a mock object for `sensor_service` (simulates event dispatching)
    mock_sensor_service = MagicMock()

    # Define a mock configuration dictionary
    config = {
        "jira_accounts": [
            {
                "name": "default",
                "username": "test_user",
                "api_token": "test_token",
                "atlassian_endpoint": "https://example-jira",
            }
        ],
        "jira_account_name": "default",  # Specifies which Jira account to use
        "jira_sensor": {},  # Placeholder (for any additional settings)
    }

    # Return a JiraIssueSensor instance with the mock sensor service and config
    return JiraIssueSensor(
        sensor_service=mock_sensor_service,
        config=config,
        poll_interval=10,
    )


@patch("jira.client.JIRA")  # Prevents real network requests to Jira
@patch("structs.jira.jira_account.JiraAccount.from_pack_config")
def test_setup(mock_from_pack_config, mock_jira_client, sensor):
    """
    Test the `setup()` method of JiraIssueSensor.

    What does this test verify?
    ---------------------------
    - Ensures `JiraAccount.from_pack_config()` is called with the correct parameters.
    - Ensures the JIRA client is initialized correctly with proper credentials.

    Why is `patch("jira.client.JIRA")` needed?
    -------------------------------------------
    - The `setup()` method creates a Jira client (`jira.client.JIRA(...)`).
    - If not patched, it would try to connect to a real Jira server, causing test failures.
    """

    # Mock JiraAccount instance
    mock_jira_account = MagicMock()
    mock_from_pack_config.return_value = mock_jira_account

    # Assign fake Jira credentials to the mock JiraAccount
    mock_jira_account.atlassian_endpoint = "https://jira.example.com"
    mock_jira_account.api_token = "mocked_token"
    mock_jira_account.username = "mocked_user"

    # Mock JIRA client instance
    mock_jira_instance = MagicMock()
    mock_jira_client.return_value = mock_jira_instance

    # Call setup() to initialize Jira credentials and JIRA client
    sensor.setup()

    # Ensure `from_pack_config()` is called with the correct arguments
    mock_from_pack_config.assert_called_once_with(
        sensor.config, sensor.config["jira_account_name"]
    )

    # Ensure JIRA client is initialized with correct parameters
    mock_jira_client.assert_called_once_with(
        server="https://jira.example.com",
        basic_auth=("mocked_user", "mocked_token"),
    )


@patch("jira.client.JIRA")  # Prevents real network requests to Jira
@patch(
    "sensors.src.jira_issue_sensor.search_issues"
)  # Mocks the Jira issue search function
@patch(
    "structs.jira.jira_account.JiraAccount.from_pack_config"
)  # Mocks Jira account retrieval
def test_poll_with_no_issues(
    mock_from_pack_config, mock_search_issues, mock_jira_client, sensor
):
    """
    Test `poll()` when `search_issues()` returns an empty list (no issues found).

    Expected behavior:
    ------------------
    - `search_issues()` should still be called with the correct parameters.
    - No triggers should be dispatched since there are no issues.

    Why do we call `sensor.setup()` in this test?
    ---------------------------------------------
    - `poll()` depends on `self.jira_account`, which is initialized in `setup()`.
    - If `setup()` is not called, `self.jira_account` does not exist, causing `AttributeError`.
    """

    # Mock JiraAccount instance
    mock_jira_account = MagicMock()
    mock_from_pack_config.return_value = mock_jira_account

    # Assign fake Jira credentials
    mock_jira_account.atlassian_endpoint = "https://jira.example.com"
    mock_jira_account.api_token = "mocked_token"
    mock_jira_account.username = "mocked_user"

    mock_jira_instance = MagicMock()
    mock_jira_client.return_value = mock_jira_instance

    # Ensure `search_issues()` returns an empty list (no issues)
    mock_search_issues.return_value = []

    # Call setup() to initialize JiraAccount and JIRA client
    sensor.setup()

    # Call poll()
    sensor.poll()

    # Ensure `search_issues()` is called correctly for each request type
    mock_search_issues.assert_any_call(
        sensor.jira_account,
        "STFCCLOUD",
        [
            'statusCategory in ("Ready For Automation")',
            '"Request Type" = "Request New Project"',
        ],
    )
    mock_search_issues.assert_any_call(
        sensor.jira_account,
        "STFCCLOUD",
        [
            'statusCategory in ("Ready For Automation")',
            '"Request Type" = "Add User"',
        ],
    )

    # Ensure no triggers were dispatched since no issues were found
    sensor.sensor_service.dispatch.assert_not_called()


@patch("jira.client.JIRA")  # Prevents real network requests to Jira
@patch(
    "sensors.src.jira_issue_sensor.search_issues"
)  # Mocks the Jira issue search function
@patch(
    "structs.jira.jira_account.JiraAccount.from_pack_config"
)  # Mocks Jira account retrieval
def test_poll_with_issues(
    mock_from_pack_config, mock_search_issues, mock_jira_client, sensor
):
    """
    Test `poll()` when `search_issues()` returns a list of Jira issues.

    Expected behavior:
    ------------------
    - `search_issues()` should be called with the correct parameters.
    - The correct triggers should be dispatched for each issue.

    Why do we call `sensor.setup()` in this test?
    ---------------------------------------------
    - `poll()` depends on `self.jira_account`, which is initialized in `setup()`.
    - If `setup()` is not called, `self.jira_account` does not exist, causing `AttributeError`.
    """

    # Mock JiraAccount instance
    mock_jira_account = MagicMock()
    mock_from_pack_config.return_value = mock_jira_account

    # Assign fake Jira credentials
    mock_jira_account.atlassian_endpoint = "https://jira.example.com"
    mock_jira_account.api_token = "mocked_token"
    mock_jira_account.username = "mocked_user"

    mock_jira_instance = MagicMock()
    mock_jira_client.return_value = mock_jira_instance

    # Mock Jira issues
    mock_issue_1 = MagicMock(key="ISSUE-101")
    mock_issue_2 = MagicMock(key="ISSUE-202")
    mock_search_issues.return_value = [mock_issue_1, mock_issue_2]

    # Call setup() to initialize JiraAccount and JIRA client
    sensor.setup()

    # Call poll()
    sensor.poll()

    # Ensure correct triggers are dispatched
    sensor.sensor_service.dispatch.assert_any_call(
        trigger="jira.request_new_project", payload={"issue_key": "ISSUE-101"}
    )
    sensor.sensor_service.dispatch.assert_any_call(
        trigger="jira.request_new_project", payload={"issue_key": "ISSUE-202"}
    )
    sensor.sensor_service.dispatch.assert_any_call(
        trigger="jira.add_user", payload={"issue_key": "ISSUE-101"}
    )
    sensor.sensor_service.dispatch.assert_any_call(
        trigger="jira.add_user", payload={"issue_key": "ISSUE-202"}
    )

    # Ensure exactly 4 dispatch calls were made (2 issues x 2 request types)
    assert sensor.sensor_service.dispatch.call_count == 4
