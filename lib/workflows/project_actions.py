from typing import Tuple

from openstack.connection import Connection
from openstack_api import openstack_project


def delete_project(
    conn: Connection, project_identifier: str, delete: bool
) -> Tuple[bool, str]:
    """
    Deletes a project
    :param conn: Openstack connection object
    :param project_identifier: (Either) The project name to delete
    :param delete: When true will delete the project, when false will only return it to reduce
                   chances of accidental deletion
    :return: The result of the operation
    """
    project = conn.identity.find_project(project_identifier, ignore_missing=False)
    project_string = "\n".join(
        f"{k}: {project.get(k, 'Not Found')}"
        for k in ["id", "name", "description", "email"]
    )

    if delete:
        delete_ok = openstack_project.delete_project(
            conn, project_identifier=project_identifier
        )
        # Currently, we only handle one error, other throws will propagate upwards
        message = f"The following project has been deleted:\n\n{project_string}"
        return delete_ok, message
    return (
        False,
        f"Tick the delete checkbox to delete the project:\n\n{project_string}",
    )
