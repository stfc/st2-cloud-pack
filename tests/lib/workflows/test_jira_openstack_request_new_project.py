from structs.jira.jira_account import JiraAccount
import pytest
from workflows.jira_openstack_request_new_project import request_new_project


def test_request_new_project_placeholder():
    """Test that request_new_project raises NotImplementedError."""
    issue_key = "TEST-123"

    with pytest.raises(NotImplementedError):
        request_new_project(JiraAccount, issue_key)
