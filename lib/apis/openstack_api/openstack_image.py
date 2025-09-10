from openstack.connection import Connection


def share_image_to_project(
    conn: Connection,
    image_identifier: str,
    project_identifier: str,
) -> None:
    """
    Shares given image with given project

    :param conn: openstack connection object
    :param image_identifier: The image name or ID that is shared with project
    :param project_identifier: Project name or ID to share image to
    """
    image = conn.image.find_image(image_identifier, ignore_missing=False)
    destination_project = conn.identity.find_project(
        project_identifier, ignore_missing=False
    )

    conn.image.add_member(image["id"], member_id=destination_project["id"])

    conn.image.update_member(destination_project["id"], image["id"], status="accepted")
