from unittest.mock import patch, MagicMock
import os
import json

import pytest
import requests
from workflows.to_webhook import to_webhook


@patch.dict(
    os.environ,
    {"ST2_ACTION_API_URL": "http://example.com", "ST2_ACTION_AUTH_TOKEN": "fake_token"},
)
@patch("requests.post")
def test_to_webhook_success(mock_post):
    """
    Test post is called with the correct parameters
    """
    webhook = "test_webhook"
    payload = [{"key1": "value1"}, {"key2": "value2"}]
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_post.return_value = mock_response

    to_webhook(webhook, payload)

    assert mock_post.call_count == 2

    mock_post.assert_any_call(
        url="http://example.com/webhooks/test_webhook",
        headers={"X-Auth-Token": "fake_token"},
        timeout=300,
        data=json.dumps({"key1": "value1"}),
        verify=False,
    )
    mock_post.assert_any_call(
        url="http://example.com/webhooks/test_webhook",
        headers={"X-Auth-Token": "fake_token"},
        timeout=300,
        data=json.dumps({"key2": "value2"}),
        verify=False,
    )


@patch.dict(
    os.environ,
    {"ST2_ACTION_API_URL": "http://example.com", "ST2_ACTION_AUTH_TOKEN": "fake_token"},
)
@patch("workflows.to_webhook.requests.post")
def test_to_webhook_failure(mock_post):
    """
    Test exception is raised if post request doesn't succeed
    """
    webhook = "test_webhook"
    payload = [{"key1": "value1"}, {"key2": "value2"}]
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        to_webhook(webhook, payload)
