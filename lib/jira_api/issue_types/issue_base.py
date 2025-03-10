from abc import ABC, abstractmethod
from typing import Dict
import jira


class IssueBase(ABC):
    """Abstract base class for all JIRA issues."""

###    def __init__(
###        self, conn: jira.client.JIRA, issue: jira.client.JIRA.issue, request_type
###    ):
###        self.request_type = request_type
###        self.id = issue.id
###        self.conn = conn
###        self.issue = issue
###        self.approved = self.get_approval()

    def __init__(
        self, conn: jira.client.JIRA, issue_key: str
    ):
        self.issue_key = issue_key
        self.conn = conn

    @abstractmethod
    def _create_properties(self) -> Dict:
        """Extract specific properties from the proforma form to use to action the issue."""

###    @property
###    def properties(self):
###        properties_dict = self._create_properties()
###        return properties_dict

###    def get_approval(self) -> bool:
###        """Extract the approval status."""
