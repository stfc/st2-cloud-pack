class MismatchedState(Exception):
    """
    Exception to be raised when the JIRA Issue is explictly expected to be
    in a different state that it actually is.
    For example, when a transition is requested from state A to state B,
    and the value A is being explicitly passed,
    but the Issue is not in that state A.
    """

    def __init__(self, issue_key, current_state):
        self.value = (
            f'The JIRA Issue "{issue_key}" is currently in state "{current_state}"'
        )

    def __str__(self):
        return repr(self.value)


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
