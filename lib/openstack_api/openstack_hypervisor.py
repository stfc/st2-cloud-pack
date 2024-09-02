from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase


class OpenstackHypervisor(OpenstackWrapperBase):
    """
    Contains the methods for interacting with the OpenStack Hypervisors
    """

    def find_hypervisor(self, cloud_account: str, search_type: str):
        """
        Runs a search for hypervisors based on the search type
        """
        return None
