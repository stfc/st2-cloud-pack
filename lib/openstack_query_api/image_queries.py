from openstackquery.api.query_objects import ImageQuery


def query_image_metadata(cloud_account: str):
    """
    Query the metadata of images
    :param cloud_account: A string representing the cloud account to use - set in clouds.ymal
    """
    metadata_query = ImageQuery()
    metadata_query.select_all()

    metadata_query.run(cloud_account=cloud_account, all_projects=True, as_admin=True)
    image_metadata = metadata_query.to_props()

    return image_metadata
