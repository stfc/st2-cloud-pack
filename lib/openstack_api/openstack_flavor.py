from typing import List, Dict, Union, Optional
from openstack.compute.v2.flavor import Flavor
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.openstack_aggregate import OpenstackAggregate

class OpenstackFlavor(OpenstackWrapperBase):

    def __init__(self, connection_cls=OpenstackConnection):
        OpenstackWrapperBase.__init__(self, connection_cls)
        self._aggregate_api = OpenstackAggregate(self._connection_cls)

    def list_flavor(self, cloud_account: str) -> List[Flavor]:
        """
        Get list of flavors from either production or development cloud
        :param cloud_account: Name of cloud to use
        :return: List of Flavor Objects
        """
        with self._connection_cls(cloud_account) as conn:
            return conn.list_flavors()

    def get_flavor(self, cloud_account: str, flavor_name: str) -> Flavor:
        """
        Get information for a specific flavor
        :param cloud_account: Name of cloud to use
        :param flavor_name: name of the flavor to get
        :return: Flavor object or None if unsuccessful
        """
        with self._connection_cls(cloud_account) as conn:
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

    def create_flavor(self, cloud_account, flavor_data) -> Flavor:
        """
        Creates a new flavor
        :param cloud_account: connection to cloud - should be dev cloud
        :param flavor_data: Flavor object from production that we want to create in dev
        :return: Flavor object or None if unsuccessful
        """

        if (
            flavor_data.swap
        ):  # openstack stores swap=0 as swap='' when getting flavor information
            flavor_swap = flavor_data.swap
        else:
            flavor_swap = 0

        with self._connection_cls(cloud_account) as conn:
            return conn.create_flavor(
                name=flavor_data.name,
                ram=flavor_data.ram,
                vcpus=flavor_data.vcpus,
                disk=flavor_data.disk,
                flavorid="auto",
                ephemeral=flavor_data.ephemeral,
                swap=flavor_swap,
                rxtx_factor=flavor_data.rxtx_factor,
                is_public=flavor_data.is_public,
            )

    def get_flavor_specs(
        self, cloud_account: str, flavor_id: Union[str, Flavor]
    ) -> Dict:
        """
        Gets the metadata for a flavor
        :param cloud_account: Cloud account to use
        :param flavor_id: The id for a flavor or the Flavor object itself
        :returns extra_specs: Dictionary containing flavor metadata
        """

        if isinstance(flavor_id, str):
            flavor = self.get_flavor(cloud_account, flavor_id)
            extra_specs = flavor.extra_specs
        else:
            extra_specs = flavor_id.extra_specs
        return extra_specs

    def set_flavor_specs(self, cloud_account: str, flavor_id: str, extra_specs: dict):
        """
        Sets extra specs for a flavor
        :param cloud_account: connection to the cloud
        :param flavor_id: ID of the flavor to add metadata to
        :param extra_specs: Dictionary of extra specs for the flavor
        """
        with self._connection_cls(cloud_account) as conn:
            if extra_specs:
                conn.set_flavor_specs(flavor_id, extra_specs)

    def migrate_flavors(
        self, source_cloud: str, dest_cloud: str
    ) -> Optional[List[str]]:
        """
        Migrates flavors from a source cloud to a destination cloud
        :param source_cloud: Cloud account used as the source for flavors
        :param dest_cloud: Cloud account for the destination for flavors
        :returns: List of missing flavor names or None if no missing flavors are found
        """
        missing_flavors = self.get_missing_flavors(source_cloud, dest_cloud)
        # if there are missing flavors in the list i.e. missing_flavors is not an empty list
        if not missing_flavors:
            return None

        for flavor_name in missing_flavors:
            flavor_data = self.get_flavor(source_cloud, flavor_name)
            dest_flavor = self.create_flavor(dest_cloud, flavor_data)
            metadata = self.get_flavor_specs(source_cloud, flavor_name)
            self.set_flavor_specs(dest_cloud, dest_flavor.id, metadata)

        return missing_flavors


    def get_all_flavors(self, cloud_account: str):
        """
        returns all flavors from the openstack instance
        :param cloud_account: connection to the cloud
        """
        with self._connection_cls(cloud_account) as conn:
            all_flavors = list(conn.compute.flavors(get_extra_specs=True))
        return all_flavors

    def find_flavors_with_hosttype(self, cloud_account: str):
        """
        filters all flavors into flavors that have aggregate_instance_extra_specs:hosttype set
        :param cloud_account: connection to the cloud
        """
        host_typed_flavors = [i for i in self.get_all_flavors(cloud_account) if "aggregate_instance_extra_specs:hosttype" in i.extra_specs]
        return host_typed_flavors

    def find_smallest_flavors(self, cloud_account: str):
        """
        create a dictionary of flavors against the hosstype flag in which the flavor selected is the smallest
        :param cloud_account: connection to the cloud
        """
        smallest_flavors = {}
        for flavors in self.find_flavors_with_hosttype(cloud_account):
            host_type = flavors["extra_specs"]["aggregate_instance_extra_specs:hosttype"]
            if host_type not in smallest_flavors:
                smallest_flavors[host_type] = flavors
            new_smallest_flavor_size = min(flavors, smallest_flavors[host_type], key=lambda flavors: flavors["ram"])
            smallest_flavors[host_type] = new_smallest_flavor_size
        return smallest_flavors

    def find_smallest_flavor_for_each_aggregate(self, cloud_account: str):
        """
        create a dictionary of aggregate against the smallest flavor for that aggregate
        :param cloud_account: connection to the cloud
        """
        aggregate_smallest_flavor = {
            aggre_objects["name"]: flavors
            for aggre_objects in self._aggregate_api.find_aggregates_with_hosttype(cloud_account)
            for flavors in self.find_smallest_flavors(cloud_account).values()
            if
            aggre_objects["metadata"]["hosttype"] == flavors["extra_specs"]["aggregate_instance_extra_specs:hosttype"]
        }
        return aggregate_smallest_flavor