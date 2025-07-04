from enum import Enum


# pylint: disable=too-few-public-methods
class Networks(Enum):
    """
    Holds a list of domains where users can be found
    """

    INTERNAL = "Internal"
    EXTERNAL = "External"
    JASMIN = "JASMIN External Cloud Network"

    @staticmethod
    def from_string(val: str):
        """
        Converts a given string in a case-insensitive way to the enum values
        """
        try:
            return Networks[val.upper()]
        except Exception as exc:
            raise NotImplementedError(f"Unknown networking type {val}") from exc
