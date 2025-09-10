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
