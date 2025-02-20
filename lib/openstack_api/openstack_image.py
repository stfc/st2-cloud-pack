from openstack.connection import Connection


def share_image_to_project(
    conn: Connection,
    image_id: str,
    project_id: str,
) -> None:
    """
    Shares given image with given project

    :param conn: openstack connection object
    :param image_id: The image ID that is shared with project
    :param project_id: Openstack ID for the project
    """
    image = conn.image.find_image(image_id, ignore_missing=False)
    destination_project = conn.identity.find_project(project_id, ignore_missing=False)

    conn.image.add_member(image["id"], member_id=destination_project["id"])

    conn.image.update_member(destination_project["id"], image["id"], status="accepted")
