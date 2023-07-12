class ParseQueryError(RuntimeError):
    """
    Exception which is thrown whenever there is an error with setting up the query - used for user-input related
    exceptions
    e.g. when inputs given are incorrect/unexpected
    """
