from abc import ABC, abstractmethod
from typing import Dict
import jira


class IssueBase(ABC):
    """Abstract base class for all JIRA issues."""

    def __init__(
        self, conn: jira.client.JIRA, issue: jira.client.JIRA.issue, request_type
    ):
        self.request_type = request_type
        self.id = issue.id
        self.conn = conn
        self.issue = issue
        self.approved = self.get_approval()

    @abstractmethod
    def _create_properties(self) -> Dict:
        """Extract specific properties from the proforma form to use to action the issue."""

    @property
    def properties(self):
        properties_dict = self._create_properties()
        return properties_dict

    def get_approval(self) -> bool:
        """Extract the approval status."""

# ==============================================================================
#
#   FIXME
#
#  replying to the ticket is an action, so it will go to actions/ directory
#
# ==============================================================================
#    def reply(self, message: str, internal: bool) -> None:
#        """
#        Reply to the ticket with a message.
#        :param message: Message to reply with.
#        :param internal: To send the message as an internal note.
#        """
#        with self.conn as conn:
#            conn.add_comment(self.id, message, internal)
