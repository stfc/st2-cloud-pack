import logging
from typing import List, Dict, Union, Optional
from openstack.connection import Connection
from openstack.compute.v2.flavor import Flavor
from openstack_api.openstack_connection import OpenstackConnection


logger = logging.getLogger(__name__)


def list_flavors(conn: Connection) -> List[Flavor]:
    """
    Get list of flavors from either production or development cloud
    :param cloud_account: Name of cloud to use
    :return: List of Flavor objects
    """
    return conn.list_flavors()


def get_flavor(cloud_account: str, flavor_name: str) -> Flavor:
    """
    Get information for a specific flavor
    :param cloud_account: Name of cloud to use
    :param flavor_name: name of the flavor to get
    :return: Flavor object or None if unsuccessful
    """
    with OpenstackConnection(cloud_account) as conn:
        return conn.get_flavor(flavor_name)


def get_missing_flavors(self, source_cloud: str, dest_cloud: str) -> List[str]:
    """
    Get list of flavors missing in Dev cloud based on the flavors currently in
    production
    :param source_cloud: Cloud account for source cloud
    :param dest_cloud: Cloud account for destination cloud
    :return: List of names of missing flavors or empty list
    """
    # list flavors from source cloud
    source_flavors = self.list_flavor(source_cloud)

    # list flavors from destination cloud
    dest_flavors = self.list_flavor(dest_cloud)

    # Prepare set of flavors in source and destination clouds
    source_flavor_names = {source.name for source in source_flavors}
    dest_flavor_names = {dest.name for dest in dest_flavors}

    # Find set of flavor names which are in source cloud but missing in the destination cloud
    missing_flavors = source_flavor_names.difference(dest_flavor_names)

    return list(missing_flavors)
