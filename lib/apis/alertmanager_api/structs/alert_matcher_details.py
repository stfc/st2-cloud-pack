from dataclasses import dataclass


@dataclass
class AlertMatcherDetails:
    name: str
    value: str

    # TODO: accept regex matchers (if needed) instead of just isEqual
    # - requires converting python regex into format AlertManager accepts
    is_equal: bool = True
    is_regex: bool = False

    def to_dict(self) -> dict:
        """
        Convert the AlertMatcherDetails to a dictionary format.
        To be used for POST actions to AlertManager API
        :return: dictionary containing stored matcher values
        """
        return {
            "isEqual": self.is_equal,
            "isRegex": self.is_regex,
            "name": self.name,
            "value": self.value,
        }

    @staticmethod
    def from_dict(data: dict) -> "AlertMatcherDetails":
        """Create an AlertMatcher instance from a dictionary."""
        return AlertMatcherDetails(
            name=data["name"],
            value=data["value"],
            is_equal=data.get("isEqual", True),
            is_regex=data.get("isRegex", False),
        )
