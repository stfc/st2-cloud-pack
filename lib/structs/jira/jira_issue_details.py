from dataclasses import dataclass
from typing import Dict, List, Optional

from enums.issue_types import IssueType


@dataclass
class IssueDetails:
    """
    Dataclass containinf fields needed to create a jira issue
    """
    project_id: str
    issue_type: IssueType
    summary: str
    description: str
    components: List[Dict[str, str]]
    epic_id: Optional[str] = None
