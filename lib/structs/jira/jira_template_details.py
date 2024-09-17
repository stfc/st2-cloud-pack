from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class JiraTemplateDetails:
    """
    This dataclass holds the template name and the parsed values to pass to template
    """

    template_name: str
    template_params: Optional[Dict[str, str]] = None
