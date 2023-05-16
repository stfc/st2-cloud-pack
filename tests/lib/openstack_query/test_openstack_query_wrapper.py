import unittest
from unittest.mock import patch, MagicMock, call
from enum import Enum, auto
from nose.tools import assert_raises

from exceptions.parse_query_error import ParseQueryError
from openstack_query.openstack_query_wrapper import OpenstackQueryWrapper


class MockedEnum(Enum):
    ITEM_1 = auto()
    ITEM_2 = auto()
    ITEM_3 = auto()
    ITEM_4 = auto()


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

        instance = self.instance.select(MockedEnum.ITEM_1, MockedEnum.ITEM_2)
        expected_query_props = {
            "property_1": 'val_1',
            "property_2": 'val_2'
        }

        mock_get_prop.assert_has_calls([
            call(MockedEnum.ITEM_1), call(MockedEnum.ITEM_2)
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

    @patch("openstack_query.openstack_query_wrapper.OpenstackQueryWrapper._get_filter_func")
    @patch("openstack_query.openstack_query_wrapper.check_filter_func")
    def test_where_valid_args(self, mock_check_filter_func, mock_get_filter_func):
        """
        Tests that where function accepts valid enum and args
        """
        preset = MockedEnum.ITEM_1
        filter_func_kwargs = MagicMock()
        mock_filter_func = MagicMock()

        expected_filter_func = mock_filter_func

        mock_check_filter_func.return_value = True
        mock_get_filter_func.return_value = mock_filter_func

        instance = self.instance.where(preset, filter_func_kwargs)

        mock_check_filter_func.assert_called_once_with(mock_filter_func, filter_func_kwargs)
        mock_get_filter_func.assert_called_once_with(preset)

        self.assertEqual(instance._filter_func, expected_filter_func)
        self.assertEqual(instance, self.instance)

    @patch("openstack_query.openstack_query_wrapper.OpenstackQueryWrapper._get_filter_func")
    @patch("openstack_query.openstack_query_wrapper.check_filter_func")
    def test_where_invalid_args(self, mock_check_filter_func, mock_get_filter_func):
        """
        Tests that where function rejects invalid args appropriately
        """
        preset = MockedEnum.ITEM_1
        filter_func_kwargs = MagicMock()
        mock_filter_func = MagicMock()

        def raise_error_side_effect(func, filter_func):
            raise TypeError("some error here")

        mock_get_filter_func.return_value = mock_filter_func
        mock_check_filter_func.side_effect = raise_error_side_effect

        with assert_raises(ParseQueryError) as err:
            _ = self.instance.where(preset, filter_func_kwargs)

        self.assertEqual(str(err.exception), "Error parsing preset args: some error here")

    @patch("openstack_query.openstack_query_wrapper.OpenstackQueryWrapper._get_filter_func")
    @patch("openstack_query.openstack_query_wrapper.check_filter_func")
    def test_where_when_already_set(self, mock_check_filter_func, mock_get_filter_func):
        filter_func_kwargs = MagicMock()
        mock_filter_func = MagicMock()

        mock_check_filter_func.return_value = True
        mock_get_filter_func.return_value = mock_filter_func

        _ = self.instance.where(MockedEnum.ITEM_1, filter_func_kwargs)

        with assert_raises(ParseQueryError) as err:
            _ = self.instance.where(MockedEnum.ITEM_2, filter_func_kwargs)

        self.assertEqual(str(err.exception), "Error: Already set a query preset")

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