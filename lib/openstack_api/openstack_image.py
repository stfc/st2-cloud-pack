from openstack.connection import Connection
from openstack.image.v2.image import Image


def get_all_image_metadata(conn: Connection):
    """
    Returns a list of images and their associated metadata
    :param conn: Openstack connection
    :type conn: Connection
    :return: List of images and their associated metadata
    """
    all_image_metadata = []

    for image in conn.image.images():
        image_metadata = {}
        image_metadata["Image ID"] = image.id
        image_metadata["Name"] = image.name
        image_metadata["Status"] = image.status
        image_metadata["Visibility"] = image.visibility
        image_metadata["Min Disk (GB)"] = image.min_disk
        image_metadata["Min RAM (MB)"] = image.min_ram
        image_metadata["OS Type"] = image.get('os_type')
        image_metadata["Metadata"] = image.properties
        all_image_metadata.append(image_metadata)

    return all_image_metadata