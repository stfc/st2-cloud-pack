from exceptions.enum_mapping_error import EnumMappingError

# pylint:disable=too-few-public-methods


class QueryPropertyMappingError(EnumMappingError):
    """
    Exception which is thrown whenever there is an error finding a property function for a given
    property Enum
    """
