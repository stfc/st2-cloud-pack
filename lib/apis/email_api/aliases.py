from typing import Dict, List

EmailAddress = str
EmailAddresses = List[EmailAddress]

# Maps name of a template to a set of kwargs that the template will use to render string output
TemplateMappings = Dict[str, Dict[str, str]]
