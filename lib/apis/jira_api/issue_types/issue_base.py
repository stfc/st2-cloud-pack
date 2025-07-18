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

    @staticmethod
    def _get_text(all_props, prop_id):
        return getattr(all_props, prop_id).text

    @staticmethod
    def _get_int(all_props, prop_id):
        return int(getattr(all_props, prop_id).text)

    @staticmethod
    def _get_adf_text(all_props, prop_id):
        content = getattr(all_props, prop_id).adf.content
        return content[0].content[0].text if content else ""

    @staticmethod
    def _get_choice(all_props, prop_id):
        return getattr(all_props, prop_id).choices[0]
