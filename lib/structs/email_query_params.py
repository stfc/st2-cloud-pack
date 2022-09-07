from dataclasses import dataclass
from typing import List, Any


@dataclass
class EmailQueryParams:
    """
    Structure containing the information needed to email users of a particular OpenstackResource
    :param: required_email_property: The name of the property that must be obtained to get the email of the
                                     user associated with the object.
    :param: valid_search_queries_no_project: List of query_preset's that can be run without a project.
    :param: search_api: API wrapper that contains the search methods that can be used
    :param: object_type: Type of object to be passed to OpenstackQuery's parse_and_output_table function
    """

    required_email_property: str
    valid_search_queries: List[str]
    valid_search_queries_no_project: List[str]
    search_api: Any
    object_type: str
