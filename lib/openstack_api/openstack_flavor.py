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
