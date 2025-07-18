from dataclasses import dataclass
from typing import Dict, List, Optional

from apis.jira_api.enums.jira_issue_types import JiraIssueType


@dataclass
class IssueDetails:
    """
    Dataclass containing fields needed to create a jira issue
    """

    project_id: str
    issue_type: JiraIssueType
    summary: str
    description: str
    components: List[Dict[str, str]]
    epic_id: Optional[str] = None
