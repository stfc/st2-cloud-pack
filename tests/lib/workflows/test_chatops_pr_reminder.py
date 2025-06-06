from unittest.mock import patch
from workflows.chatops_pr_reminder import pr_reminder


@patch("workflows.chatops_pr_reminder.requests")
def test_pr_reminder(mock_requests) -> None:
    """Test PR reminder runs successfully with correct arguments."""
    mock_endpoint = "https://mock.url/endpoint"
    mock_token = "mock_token"
    mock_channel = "mock_channel"
    mock_reminder_type = "mock_reminder_type"
    res = pr_reminder(mock_endpoint, mock_token, mock_channel, mock_reminder_type)
    mock_response = mock_requests.post.return_value
    mock_headers = {
        "Content-Type": "application/json",
        "Authorization": f"token {mock_token}",
    }
    mock_body = {"reminder_type": mock_reminder_type, "channel": mock_channel}
    mock_requests.post.assert_called_once_with(
        mock_endpoint, json=mock_body, headers=mock_headers, timeout=120
    )
    mock_response.raise_for_status.assert_called_once()
    assert res == {
        "status_code": mock_response.status_code,
        "response": mock_response.text,
    }
