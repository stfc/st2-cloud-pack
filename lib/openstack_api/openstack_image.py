from typing import Dict, List
from openstack.connection import Connection

def get_image_metadata(conn: Connection) -> List[Dict]:
    """
    Returns metadata for the available images
    :param conn: openstack connection object
    :type conn: Connection
    :return: List of images and their associated metadata
    :rtype: List[Dict]
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
        image_metadata["OS Type"] = image.os_type
        image_metadata["Metadata"] = image.properties
        all_image_metadata.append(image_metadata)

    return all_image_metadata
