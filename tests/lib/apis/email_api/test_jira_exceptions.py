"""
Custom made Exceptions specific for failures in the interaction
with the JIRA server
"""

from apis.jira_api.exceptions.jira_forbidden_transition import ForbiddenTransition
from apis.jira_api.exceptions.jira_mismatched_state import MismatchedState


def test_mismatched_state_exception():
    """
    Tests that MismatchedState exception initializes and returns the expected message
    """
    exception = MismatchedState("ISSUE-123", "In Progress")

    msg = 'The JIRA Issue "ISSUE-123" is currently in state "In Progress"'
    assert str(exception) == repr(msg)


def test_forbidden_transition_exception():
    """
    Tests that ForbiddenTransition exception initializes and returns the expected message
    """
    exception = ForbiddenTransition("ISSUE-456", "Closed")

    msg = 'The JIRA Issue "ISSUE-456" is not in any state allowing a transition to "Closed"'
    assert str(exception) == repr(msg)
