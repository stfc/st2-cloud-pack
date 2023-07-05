from typing import List, Dict, Callable, Any

from openstack.compute.v2.aggregate import Aggregate
from openstack.compute.v2.hypervisor import Hypervisor

from openstack_api.openstack_hypervisor import OpenstackHypervisor
from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_query_base import OpenstackQueryBase
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase

class OpenstackAggregate(OpenstackWrapperBase, OpenstackQueryBase):
    def __init__(self, connection_cls=OpenstackConnection):
        OpenstackWrapperBase.__init__(self, connection_cls)
        self._hypervisor_api = OpenstackHypervisor(self._connection_cls)

    def get_all_aggregates(self, cloud_account: str):
        """
        returns all aggregates from the openstack instance
        :param cloud_account: The associated clouds.yaml account
        """
        with self._connection_cls(cloud_account) as conn:
            all_aggregates = list(conn.compute.aggregates(get_extra_specs=True))
        return all_aggregates


    def find_aggregates_with_hosttype(self, cloud_account: str):
        """
        filters all aggregates into aggregates with hosttype set
        :param cloud_account: The associated clouds.yaml account
        """
        host_typed_aggregates: List[Aggregate] = [i for i in self.get_all_aggregates(cloud_account) if
                                                  "hosttype" in i.metadata]
        return host_typed_aggregates

    def create_dictionary_of_aggregates_to_hostnames(self, cloud_account:str):
        """
        create a dictionary of aggregate against a list of hypervisor hostnames
        :param cloud_account: The associated clouds.yaml account
        """
        dict_of_hv_names: Dict[Aggregate, List[str]] = {}
        for aggres in self.find_aggregates_with_hosttype(cloud_account):
            aggregate_name = aggres["name"]
            dict_of_hv_names[aggregate_name] = aggres["hosts"]
        return dict_of_hv_names

    def create_dict_of_aggregate_to_hv_objects(self, cloud_account: str):
        """
        create a dictionary of aggregate against all of its hypervisor objects
        :param cloud_account: The associated clouds.yaml account
        """
        hv_names: Dict[Aggregate, List[Hypervisor]] = {}
        for aggregate, hv_hostnames in self.create_dictionary_of_aggregates_to_hostnames(cloud_account):
            find_hvs = [i for i in self._hypervisor_api.list_alll_hv_objects(cloud_account) if i.name in hv_hostnames]
            hv_names[aggregate] = find_hvs
        return hv_names