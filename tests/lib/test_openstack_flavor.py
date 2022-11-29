import unittest
from unittest.mock import NonCallableMock, Mock, MagicMock, call
from openstack_api.openstack_flavor import OpenstackFlavor


# pylint:disable=too-many-public-methods
class OpenstackFlavorTests(unittest.TestCase):
    """
    Runs various tests to ensure we are using the Openstack
    Flavor module in the expected way
    """

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = OpenstackFlavor(self.mocked_connection)
        self.api = self.mocked_connection.return_value.__enter__.return_value

    def test_list_flavor(self):
        """
        Test that we can retrieve a list of flavors from a specific cloud
        """
        mocked_cloud_name = NonCallableMock()
        flavors = self.instance.list_flavor(mocked_cloud_name)

        assert flavors == self.api.list_flavors.return_value

        self.api.list_flavors.assert_called_once_with()
        self.mocked_connection.assert_called_once_with(mocked_cloud_name)

    def test_get_flavor(self):
        """
        Test that we can get information for a specific flavor
        """
        mocked_cloud_name = NonCallableMock()
        mocked_flavor_name = NonCallableMock()
        flavor = self.instance.get_flavor(mocked_cloud_name, mocked_flavor_name)

        assert flavor == self.api.get_flavor.return_value

        self.api.get_flavor.assert_called_once_with(mocked_flavor_name)
        self.mocked_connection.assert_called_once_with(mocked_cloud_name)

    def test_get_missing_flavors_calls_list_flavor(self):
        """
        Test that we are passing the source and destination clouds in the correct order
        in order to list flavors from each cloud
        """
        source_cloud, dest_cloud = NonCallableMock(), NonCallableMock()
        self.instance.list_flavor = Mock(return_value=[])
        self.instance.get_missing_flavors(source_cloud, dest_cloud)
        self.instance.list_flavor.assert_has_calls(
            [call(source_cloud), call(dest_cloud)],
            any_order=False,  # Order matters here
        )

    def test_get_missing_flavors_get_diff(self):
        """
        Test getting the difference between list of flavor names
        """
        # create set 1 = [0, 1, 2]
        mock_source_names = [NonCallableMock() for _ in range(3)]
        for i, obj in enumerate(mock_source_names):
            obj.name = i
        # create set 2 = [2, 3, 4]
        mock_dest_names = [NonCallableMock() for _ in range(3)]
        for i, obj in enumerate(mock_dest_names):
            obj.name = i + 2

        mock_side_effect = [mock_source_names, mock_dest_names]

        self.instance.list_flavor = Mock(side_effect=mock_side_effect)
        return_diff = self.instance.get_missing_flavors(
            NonCallableMock(), NonCallableMock()
        )
        # expect [0,1] as elements are in set 1 but are missing from set 2
        assert [0, 1] == return_diff

    def test_create_flavor(self):
        """
        Test we can create a new flavor
        """
        mocked_cloud_name = NonCallableMock()
        mocked_flavor_data = NonCallableMock()

        self.instance.create_flavor(mocked_cloud_name, mocked_flavor_data)
        self.mocked_connection.assert_called_once_with(mocked_cloud_name)

        self.api.create_flavor.assert_called_once_with(
            name=mocked_flavor_data.name,
            ram=mocked_flavor_data.ram,
            vcpus=mocked_flavor_data.vcpus,
            disk=mocked_flavor_data.disk,
            flavorid="auto",
            ephemeral=mocked_flavor_data.ephemeral,
            swap=mocked_flavor_data.swap,
            rxtx_factor=mocked_flavor_data.rxtx_factor,
            is_public=mocked_flavor_data.is_public,
        )

    def test_empty_dict(self):
        """
        Test that method set_flavor_specs not called when empty_dictionary passed
        """
        empty_flavor_spec = {}
        mocked_cloud_name = NonCallableMock()
        flavor_id = NonCallableMock()
        self.instance.set_flavor_specs(mocked_cloud_name, flavor_id, empty_flavor_spec)
        self.api.set_flavor_specs.assert_not_called()

    def test_flavor_id_get_specs(self):
        """
        Test getting the extra specs from a flavor
        """
        mocked_cloud_name = NonCallableMock()
        mocked_flavor_id = NonCallableMock()

        flavor = self.instance.get_flavor(
            cloud_account=mocked_cloud_name, flavor_name=mocked_flavor_id
        )

        assert flavor == self.api.get_flavor.return_value
        self.api.get_flavor.assert_called_once_with(mocked_flavor_id)

    def test_flavor_object_get_specs(self):
        """
        Test getting the extra specs from a flavor
        """
        mocked_cloud_name = NonCallableMock()
        mocked_flavor = NonCallableMock()

        extra_specs = Mock()
        self.instance.get_flavor_specs = Mock()

        self.instance.get_flavor_specs.return_value = extra_specs

        self.instance.get_flavor_specs(mocked_cloud_name, mocked_flavor)

        self.instance.get_flavor_specs.assert_called_once_with(
            mocked_cloud_name, mocked_flavor
        )

    def test_set_specs(self):
        """
        Test setting the extra specs for a flavor
        """
        mocked_cloud_name = NonCallableMock()
        flavor_id = NonCallableMock()
        extra_specs = NonCallableMock()

        self.instance.set_flavor_specs(mocked_cloud_name, flavor_id, extra_specs)
        self.mocked_connection.assert_called_once_with(mocked_cloud_name)
        self.api.set_flavor_specs.assert_called_once_with(flavor_id, extra_specs)

    def test_empty_list_migrate_flavors(self):
        """
        Test case when there is an empty list in migrate_flavors
        """
        mocked_source_cloud = NonCallableMock()
        mocked_dest_cloud = NonCallableMock()
        missing_flavors = NonCallableMock()

        self.instance.get_missing_flavors = Mock()
        self.instance.get_flavor = Mock()

        self.instance.get_missing_flavors.return_value = missing_flavors

        self.instance.get_missing_flavors(mocked_source_cloud, mocked_dest_cloud)
        self.instance.get_missing_flavors.assert_called_once_with(
            mocked_source_cloud, mocked_dest_cloud
        )
        self.instance.get_flavor.assert_not_called()

    def test_missing_flavors_migrate_flavors(self):
        """
        Test migration of flavors
        """
        mocked_source_cloud = NonCallableMock()
        mocked_dest_cloud = NonCallableMock()

        flavors = ["flavor 0", "flavor 1", "flavor 2"]
        self.instance.get_missing_flavors = Mock(return_value=flavors)

        self.instance.get_flavor = Mock()
        self.instance.create_flavor = Mock()
        self.instance.get_flavor_specs = Mock()
        self.instance.set_flavor_specs = Mock()

        self.instance.migrate_flavors(mocked_source_cloud, mocked_dest_cloud)

        self.instance.get_flavor.assert_has_calls(
            [call(mocked_source_cloud, flavor) for flavor in flavors]
        )

        self.instance.create_flavor.assert_has_calls(
            [
                call(mocked_dest_cloud, self.instance.get_flavor.return_value)
                for _ in flavors
            ]
        )

        self.instance.get_flavor_specs.assert_has_calls(
            [call(mocked_source_cloud, flavor) for flavor in flavors]
        )

        self.instance.set_flavor_specs(
            [
                call(
                    mocked_dest_cloud,
                    self.instance.create_flavor.return_value.id,
                    self.instance.get_flavor_specs.return_value,
                )
                for _ in flavors
            ]
        )
