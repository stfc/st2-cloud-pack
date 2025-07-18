from enum import auto
from meta.enums.auto_name import _AutoName


# pylint: disable=too-few-public-methods
class JiraIssueType(_AutoName):
    TASK = auto()
    EPIC = auto()
    BUG = auto()
