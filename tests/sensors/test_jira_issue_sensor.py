from unittest.mock import MagicMock, patch
import pytest
from sensors.src.jira_issue_sensor import JiraIssueSensor


def test_sensor_initialization_with_no_config():
    """
    Test `__init__()` when no config is provided.

    Expected behavior:
    ------------------
    - If `config` is None or empty, `__init__()` should raise a `ValueError`
      with the message "No config found for sensor".
    """
    with pytest.raises(ValueError, match="No config found for sensor"):
        JiraIssueSensor(sensor_service=MagicMock(), config=None)

    with pytest.raises(ValueError, match="No config found for sensor"):
        JiraIssueSensor(sensor_service=MagicMock(), config={})


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


@patch("structs.jira.jira_account.JiraAccount.from_pack_config")  # Mock JiraAccount
def test_sensor_initialization(mock_from_pack_config):
    """
    Test `__init__()` method of JiraIssueSensor.

    What does this test verify?
    ---------------------------
    - Ensures `JiraAccount.from_pack_config()` is called when the sensor is created.
    - Ensures `self.endpoint`, `self.token`, and `self.username` are correctly assigned.

    Why is `patch("JiraAccount.from_pack_config")` needed?
    ------------------------------------------------------
    - Since `__init__()` calls `from_pack_config()`, we must mock it to prevent real config lookups.
    """

    # Mock JiraAccount instance
    mock_jira_account = MagicMock()
    mock_jira_account.atlassian_endpoint = "https://jira.example.com"
    mock_jira_account.api_token = "mocked_token"
    mock_jira_account.username = "mocked_user"

    # Make `from_pack_config()` return our mock JiraAccount
    mock_from_pack_config.return_value = mock_jira_account

    # Create a new sensor instance (this will automatically trigger `__init__()`)
    sensor = JiraIssueSensor(
        sensor_service=MagicMock(), config={"jira_account_name": "default"}
    )

    # Ensure `from_pack_config()` was called correctly
    mock_from_pack_config.assert_called_once_with(sensor.config, "default")

    # Ensure attributes are correctly assigned
    assert sensor.endpoint == "https://jira.example.com"
    assert sensor.token == "mocked_token"
    assert sensor.username == "mocked_user"


@patch("jira.client.JIRA")  # Prevents real network requests to Jira
def test_setup(mock_jira_client, sensor):
    """
    Test the `setup()` method of JiraIssueSensor.

    What does this test verify?
    ---------------------------
    - Ensures `setup()` initializes the JIRA client (`self.jira_client`).
    - Ensures the JIRA client is created with correct authentication parameters.

    Why is `patch("jira.client.JIRA")` needed?
    -------------------------------------------
    - The `setup()` method creates a Jira client (`jira.client.JIRA(...)`).
    - If not patched, it would try to connect to a real Jira server, causing test failures.
    """

    # Mock JIRA client instance
    mock_jira_instance = MagicMock()
    mock_jira_client.return_value = mock_jira_instance

    # Call setup() to initialize the JIRA client
    sensor.setup()

    # Ensure JIRA client is initialized with correct parameters
    mock_jira_client.assert_called_once_with(
        server=sensor.endpoint,
        basic_auth=(sensor.username, sensor.token),
    )

    # Ensure the sensor's `jira_client` is assigned
    assert sensor.jira_client == mock_jira_instance


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
        "DCTE",
        [
            'status = "Ready For Automation"',
            '"Request Type" = "Request New Project"',
        ],
    )
    mock_search_issues.assert_any_call(
        sensor.jira_account,
        "DCTE",
        [
            'status = "Ready For Automation"',
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


@patch("jira.client.JIRA")  # Prevents real network requests
def test_cleanup(mock_jira_client, sensor):
    """
    Test the `cleanup()` method of JiraIssueSensor.

    Expected behavior:
    ------------------
    - If `self.jira_client` exists, `cleanup()` should call `self.jira_client.close()`.
    - `self.jira_client` should be set to `None` after cleanup.
    """

    # Mock JIRA client instance and set it to sensor
    mock_jira_instance = MagicMock()
    mock_jira_client.return_value = mock_jira_instance

    # Ensure `setup()` is called to initialize `jira_client`
    sensor.setup()

    # Call cleanup()
    sensor.cleanup()

    # Ensure `close()` was called on the `jira_client`
    mock_jira_instance.close.assert_called_once()

    # Ensure `jira_client` is set to None
    assert sensor.jira_client is None


def test_cleanup_when_jira_client_is_none(sensor):
    """
    Test `cleanup()` when `self.jira_client` is already `None`.

    Expected behavior:
    ------------------
    - `cleanup()` should not raise an error.
    - `self.jira_client` should remain `None`.
    """

    # Ensure `jira_client` is None before cleanup
    sensor.jira_client = None

    # Call cleanup()
    sensor.cleanup()

    # Ensure `jira_client` is still None
    assert sensor.jira_client is None
