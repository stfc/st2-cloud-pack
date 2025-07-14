class ForbiddenTransition(Exception):
    """
    Exception to be raised when there is a desire to move a JIRA Issue
    to a different state it current is in,
    but that state is not reachable according that the Issue workflow.
    """

    def __init__(self, issue_key, to_state):
        self.value = f'The JIRA Issue "{issue_key}" is not in any state allowing a transition to "{to_state}"'

    def __str__(self):
        return repr(self.value)
