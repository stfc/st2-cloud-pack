import unittest
from unittest.mock import patch, MagicMock, call
from openstack_query.openstack_query_wrapper import OpenstackQueryWrapper
from enum import Enum, auto


class MockedEnum(Enum):
    PROP_1 = auto()
    PROP_2 = auto()
    PROP_3 = auto()
    PROP_4 = auto()


class OpenstackQueryWrapperTests(unittest.TestCase):
    """
    Runs various tests to ensure that OpenstackQueryWrapper functions expectedly.
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = OpenstackQueryWrapper(connection_cls=self.mocked_connection)
        self.conn = self.mocked_connection.return_value.__enter__.return_value

    @patch("openstack_query.openstack_query_wrapper.OpenstackQueryWrapper._get_prop")
    def test_select(self, mock_get_prop):
        """
        Tests that select function accepts all valid property Enums and sets attribute appropriately
        """
        mock_get_prop.side_effect = [
            ("property_1", 'val_1'),
            ("property_2", 'val_2')
        ]

        instance = self.instance.select(MockedEnum.PROP_1, MockedEnum.PROP_2)
        expected_query_props = {
            "property_1": 'val_1',
            "property_2": 'val_2'
        }

        mock_get_prop.assert_has_calls([
            call(MockedEnum.PROP_1), call(MockedEnum.PROP_2)
        ])
        self.assertEqual(instance._query_props, expected_query_props)
        self.assertEqual(instance, self.instance)

    @patch("openstack_query.openstack_query_wrapper.OpenstackQueryWrapper._get_all_props")
    def test_select_all(self, mock_get_all_props):
        """
        Tests that select_all function sets attribute to use all valid properties
        """
        expected_query_props = {
            "property_1": 'value_1',
            "property_2": 'value_2',
            "property_3": 'value_3'
        }

        mock_get_all_props.return_value = {
            "property_1": 'value_1',
            "property_2": 'value_2',
            "property_3": 'value_3'
        }

        instance = self.instance.select_all()
        mock_get_all_props.assert_called_once()
        self.assertEqual(instance._query_props, expected_query_props)
        self.assertEqual(instance, self.instance)

    def test_where_valid_args(self):
        """
        Tests that where function accepts valid enum and args
        """
        raise NotImplementedError

    def test_where_invalid_args(self):
        """
        Tests that where function rejects invalid args appropriately
        """
        raise NotImplementedError

    def test_run_valid(self):
        """
        Tests that run function sets up query and calls _run_query appropriately
        """
        raise NotImplementedError

    def test_run_incomplete_conf(self):
        """
        Tests that run function catches when config is incomplete
        """
        raise NotImplementedError

    def test_group_by(self):
        """
        Tests that group groups results into list of lists appropriately
        """
        raise NotImplementedError

    def test_sort_by(self):
        """
        Tests that sort_by function sorts results list appropriately
        """
        raise NotImplementedError

    def test_to_list(self):
        """
        Tests that to_list function returns correct values
        """
        raise NotImplementedError

    def test_to_html(self):
        """
        Tests that to_html function returns correct value
        """
        raise NotImplementedError

    def test_to_string(self):
        """
        Tests that to_string function returns correct value
        """
        raise NotImplementedError