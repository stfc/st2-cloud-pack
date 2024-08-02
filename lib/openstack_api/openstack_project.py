from typing import List, Optional, Callable
import re

from openstack.connection import Connection
from openstack.exceptions import ConflictException
from openstack.identity.v3.project import Project

from exceptions.missing_mandatory_param_error import MissingMandatoryParamError
from structs.project_details import ProjectDetails


def create_project(
    conn: Connection, project_details: ProjectDetails
) -> Optional[Project]:
    """
    Creates a given project with the provided details
    :param conn: openstack connection object
    :param project_details: A datastructure containing all the project details
    :return: A clouds project, or None if it was unsuccessful
    """
    # domain_id can be blank, we will create a project in the default domain
    if not project_details.name:
        raise MissingMandatoryParamError("The project name is missing")
    if not project_details.email:
        raise MissingMandatoryParamError("The project contact email is missing")
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_regex, project_details.email):
        raise ValueError("The project contact email is invalid")

    create_project_kwargs = {
        "name": project_details.name,
        "description": project_details.description,
        "is_enabled": project_details.is_enabled,
    }
    if project_details.parent_id:
        create_project_kwargs["parent_id"] = project_details.parent_id

    tags = [project_details.email]
    if project_details.immutable:
        tags.append("immutable")
    create_project_kwargs["tags"] = tags

    try:
        return conn.identity.create_project(**create_project_kwargs)
    except ConflictException as err:
        # Strip out frames that are noise by rethrowing
        raise ConflictException(err.message) from err


def delete_project(conn: Connection, project_identifier: str) -> bool:
    """
    Deletes a project from Openstack default domain
    :param conn: openstack connection object
    :param project_identifier: The name or Openstack ID for the project
    :return: True if the project was deleted, False if the operation failed
    """
    project = conn.identity.find_project(
        project_identifier=project_identifier, ignore_missing=False
    )

    if _is_project_immutable(project):
        raise ValueError("Project is immutable and so can't be deleted")

    result = conn.identity.delete_project(project=project, ignore_missing=False)
    return result is None  # Where None == success


def _find_project_tag(
    project_tags: List[str], select_func: Callable[[str], bool]
) -> Optional[str]:
    """
    Returns the index of a project tag matching a given query
    :param project_tags: The project tags
    :param select_func: Function that determines whether a tag should be selected
    :return: The tag found or None
    """
    tag_index = _find_project_tag_index(project_tags, select_func)
    if tag_index is not None:
        return project_tags[tag_index]
    return None


def _find_project_tag_index(
    project_tags: List[str], select_func: Callable[[str], bool]
) -> Optional[int]:
    """
    Returns the index of a project tag matching a given query
    :param project_tags: The project tags
    :param select_func: Function that determines whether a tag should be selected
    :return: The index of found tag or None
    """
    for i, project_tag in enumerate(project_tags):
        if select_func(project_tag):
            return i
    return None


def _is_project_immutable(project: Project) -> bool:
    """
    Returns whether a given project is immutable or not
    :param project: The project to check
    :return: Whether the project is immutable
    """
    return _find_project_tag(project["tags"], _select_project_immutable) == "immutable"


def _select_project_immutable(tag) -> bool:
    return tag == "immutable"
