class QueryPresetMappingError(RuntimeError):
    """
    Exception which is thrown whenever there is an error finding a client-side or server-side filter for a given
    preset-property pair
    """
