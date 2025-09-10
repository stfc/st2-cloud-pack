from abc import ABC, abstractmethod
from typing import Dict
import jira


class IssueBase(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for all JIRA issues."""

    def __init__(self, conn: jira.client.JIRA, issue_key: str):
        self.issue_key = issue_key
        self.conn = conn

    @abstractmethod
    def _create_properties(self) -> Dict:
        """Extract specific properties from the proforma form to use to action the issue."""

    @property
    def properties(self):
        return self._create_properties()
