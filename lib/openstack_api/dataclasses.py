from dataclasses import dataclass
from typing import Any, Callable, List

from openstack.connection import Connection
from openstack.identity.v3.project import Project


@dataclass
class NonExistentCheckParamsBase:
    """
    Contains the data needed for running OpenstackQuery.find_non_existent_...
    :param object_id_param_name: Name of the parameter that contains the object id in the objects returned by
                                'object_list_func' in the below dataclasses
    :param object_project_param_name: Name of the parameter that contains the project id in the objects returned
                                      by 'object_list_func' in the below dataclasses
    """

    object_id_param_name: str
    object_project_param_name: str


@dataclass
class NonExistentCheckParams(NonExistentCheckParamsBase):
    """
    Contains the data needed for running OpenstackQuery.find_non_existent_objects
    :param object_list_func: Function that takes the connection and project and should return all instances
                                of the chosen openstack object in that project as a list
    :param object_get_func: Function that takes the connection and an openstack object id and should attempt
                            to get that object (Throwing an openstack.exceptions.ResourceNotFound error if it
                            fails)
    """

    object_list_func: Callable[[Connection, Project], List]
    object_get_func: Callable[[Connection, str], Any]


@dataclass
class NonExistentProjectCheckParams(NonExistentCheckParamsBase):
    """
    Contains the data needed for running OpenstackQuery.find_non_existant_object_projects
    :param object_list_func: Function that takes the connection and should return all instances
                             of the chosen openstack object in that project as a list
    """

    object_list_func: Callable[[Connection], List]


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


@dataclass
class QueryParams:
    """
    Contains the data needed for running OpenstackQuery.search_resource
    :param query_preset: The query to use when searching
    :param properties_to_select: The properties to select and display from the found resource
    :param group_by: Property to group the results by - can be empty for no grouping
    :param return_html: Whether the result should be in html format or not
    """

    query_preset: str
    properties_to_select: List[str]
    group_by: str
    return_html: bool
