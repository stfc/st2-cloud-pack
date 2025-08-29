import logging
from typing import List
from openstack.compute.v2.flavor import Flavor
from openstack_api.openstack_connection import OpenstackConnection


logger = logging.getLogger(__name__)


class OpenstackFlavor:
    def list_flavors(self, cloud_account: str) -> List[Flavor]:
        """
        Get list of flavors from either the prod or dev cloud
        :param cloud_account: Name of cloud to use
        :return: List of Flavor objects
        """
        with OpenstackConnection(cloud_account) as conn:
            return conn.list_flavors()

    def get_missing_flavors(self, source_cloud: str, dest_cloud: str) -> List[str]:
        """
        Get list of flavors missing in the dev cloud based on the flavors currently in
        the prod cloud
        :param source_cloud: The source cloud from which the sensor will apply updates
        :param dest_cloud: The destination cloud which the sensor will apply any required updates to
        :return: List of names of missing flavors or empty list
        """
        # # list flavors from source cloud
        # source_flavors = self.list_flavors(source_cloud)

        # list flavors from destination cloud
        source_flavors = self.list_flavors(dest_cloud)
        dest_flavors = self.list_flavors(dest_cloud)[0]

        # Prepare set of flavors in source and destination clouds
        source_flavor_names = {source.name for source in source_flavors}
        dest_flavor_names = {dest.name for dest in dest_flavors}

        # Find set of flavor names which are in source cloud but missing in the destination cloud
        missing_flavors = source_flavor_names.difference(dest_flavor_names)

        return list(missing_flavors)
