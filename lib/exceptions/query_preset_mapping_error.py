from exceptions.enum_mapping_error import EnumMappingError


class QueryPresetMappingError(EnumMappingError):
    """
    Exception which is thrown whenever there is an error finding a client-side or server-side filter for a given
    preset-property pair
    """
