from unittest.mock import MagicMock, patch
from jira_api.jira_issue import JiraConnection


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
