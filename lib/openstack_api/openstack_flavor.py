from typing import List, Dict, Union, Optional
from openstack.compute.v2.flavor import Flavor
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase


class OpenstackFlavor(OpenstackWrapperBase):
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
