import unittest
from unittest.mock import patch, MagicMock, call, NonCallableMock
from enum import Enum, auto
from nose.tools import assert_raises, raises

from enums.query.query_presets import QueryPresets

from exceptions.parse_query_error import ParseQueryError
from openstack_query.query_wrapper import QueryWrapper


class MockedEnum(Enum):
    ITEM_1 = auto()
    ITEM_2 = auto()
    ITEM_3 = auto()
    ITEM_4 = auto()


class QueryWrapperTests(unittest.TestCase):
    """
    Runs various tests to ensure that QueryWrapper functions expectedly.
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = QueryWrapper(connection_cls=self.mocked_connection)
        self.conn = self.mocked_connection.return_value.__enter__.return_value

    @patch("openstack_query.query_wrapper.QueryWrapper._get_prop")
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

    @patch("openstack_query.query_wrapper.QueryWrapper._PROPERTY_MAPPINGS")
    def test_get_prop(self, mocked_property_mappings):
        """
        Tests that get_prop function functions expectedly
        """
        prop_mappings = {MockedEnum.ITEM_1: 'some_func'}
        mocked_property_mappings.keys.return_value = [MockedEnum.ITEM_1]
        mocked_property_mappings.__getitem__.side_effect = prop_mappings.__getitem__

        res = self.instance._get_prop(MockedEnum.ITEM_1)
        mocked_property_mappings.keys.assert_called_once()
        mocked_property_mappings.__getitem__.assert_called_once_with(MockedEnum.ITEM_1)
        self.assertEqual(res, ('item_1', 'some_func'))

    @patch("openstack_query.query_wrapper.QueryWrapper._get_all_props")
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

    @patch("openstack_query.query_wrapper.QueryWrapper._PROPERTY_MAPPINGS")
    def test_get_all_props(self, mocked_property_mappings):
        mocked_property_mappings.items.return_value = [
            (MockedEnum.ITEM_1, 'some_func_1'),
            (MockedEnum.ITEM_2, 'some_func_2'),
            (MockedEnum.ITEM_3, 'some_func_3'),
            (MockedEnum.ITEM_4, 'some_func_4')
        ]

        res = self.instance._get_all_props()
        mocked_property_mappings.items.assert_called_once()
        self.assertEqual(res, {
            'item_1': 'some_func_1',
            'item_2': 'some_func_2',
            'item_3': 'some_func_3',
            'item_4': 'some_func_4'
        })

    @patch("openstack_query.query_wrapper.QueryWrapper._get_filter_func")
    @patch("openstack_query.query_wrapper.check_filter_func")
    def test_where_valid_args(self, mock_check_filter_func, mock_get_filter_func):
        """
        Tests that where function accepts valid enum and args
        """
        preset = MockedEnum.ITEM_1
        prop = MockedEnum.ITEM_2
        filter_func_kwargs = MagicMock()
        mock_filter_func = MagicMock()

        expected_filter_func = mock_filter_func

        mock_check_filter_func.return_value = True
        mock_get_filter_func.return_value = mock_filter_func

        instance = self.instance.where(preset, prop, filter_func_kwargs)

        filter_func_kwargs.update.assert_called_once_with({'prop':prop})
        mock_check_filter_func.assert_called_once_with(mock_filter_func, filter_func_kwargs)
        mock_get_filter_func.assert_called_once_with(preset, prop)

        self.assertEqual(instance._filter_func, expected_filter_func)
        self.assertEqual(instance, self.instance)

    @patch("openstack_query.query_wrapper.QueryWrapper._get_filter_func")
    @patch("openstack_query.query_wrapper.check_filter_func")
    def test_where_invalid_args(self, mock_check_filter_func, mock_get_filter_func):
        """
        Tests that where function rejects invalid args appropriately
        """
        preset = MockedEnum.ITEM_1
        prop = MockedEnum.ITEM_2
        filter_func_kwargs = MagicMock()
        mock_filter_func = MagicMock()

        def raise_error_side_effect(func, filter_func):
            raise TypeError("some error here")

        mock_get_filter_func.return_value = mock_filter_func
        mock_check_filter_func.side_effect = raise_error_side_effect

        with assert_raises(ParseQueryError) as err:
            _ = self.instance.where(preset, prop, filter_func_kwargs)

        self.assertEqual(str(err.exception), "Error parsing preset args: some error here")

    @patch("openstack_query.query_wrapper.QueryWrapper._get_filter_func")
    @patch("openstack_query.query_wrapper.check_filter_func")
    def test_where_when_already_set(self, mock_check_filter_func, mock_get_filter_func):
        """
        Tests that where function fails noisily when re-instantiated
        """
        filter_func_kwargs = MagicMock()
        mock_filter_func = MagicMock()

        mock_check_filter_func.return_value = True
        mock_get_filter_func.return_value = mock_filter_func

        _ = self.instance.where(MockedEnum.ITEM_1, MockedEnum.ITEM_2, filter_func_kwargs)

        with assert_raises(ParseQueryError) as err:
            _ = self.instance.where(MockedEnum.ITEM_3, MockedEnum.ITEM_4, filter_func_kwargs)

        self.assertEqual(str(err.exception), "Error: Already set a query preset")

    @patch("openstack_query.query_wrapper.QueryWrapper._run_query")
    @patch("openstack_query.query_wrapper.QueryWrapper._apply_filter_func")
    @patch("openstack_query.query_wrapper.QueryWrapper._parse_properties")
    def test_run_valid(self, mock_parse_properties, mock_apply_filter_func, mock_run_query):
        """
        Tests that run function sets up query and calls _run_query appropriately
        """
        query_props = {
            'prop1': 'prop_func1', 'prop2': 'prop_func2', 'prop3': 'prop_func3'
        }
        filter_func = MagicMock()
        res_out = ['obj1', 'obj2', 'obj3']
        filter_out = ['obj1', 'obj2']
        parse_out = ['parse_out1', 'parse_out2']

        self.instance._query_props = query_props
        self.instance._filter_func = filter_func

        mock_run_query.return_value = res_out
        mock_apply_filter_func.return_value = filter_out
        mock_parse_properties.return_value = parse_out

        instance = self.instance.run(cloud_account="test")
        self.mocked_connection.assert_called_once_with("test")

        mock_run_query.assert_called_once_with(self.conn)
        mock_apply_filter_func.assert_called_once_with(res_out, filter_func)
        mock_parse_properties.assert_called_once_with(filter_out, query_props)

        self.assertEqual(parse_out, instance._results)
        self.assertEqual(instance, self.instance)

    @raises(RuntimeError)
    def test_run_incomplete_conf(self):
        """
        Tests that run function catches when config is incomplete
        """
        self.instance._query_props = []
        _ = self.instance.run(cloud_account="test")

    @patch("openstack_query.query_wrapper.QueryWrapper._parse_property")
    def test_parse_properties(self, mock_parse_property):
        """
        Tests that parse_properties function works expectedly with 0, 1 and 2 items
        """
        item_1 = 'openstack-resource-1'
        item_2 = 'openstack-resource-2'
        property_funcs = MagicMock()

        # 0 items
        assert not self.instance._parse_properties([], property_funcs)

        # 1 item
        _ = self.instance._parse_properties([item_1], property_funcs)
        mock_parse_property.assert_called_once_with(item_1, property_funcs)

        # 2 items
        _ = self.instance._parse_properties([item_1, item_2], property_funcs)
        mock_parse_property.assert_has_calls([
            call(item_1, property_funcs), call(item_2, property_funcs)
        ])

    @patch("openstack_query.query_wrapper.QueryWrapper._run_prop_func")
    def test_parse_property(self, mock_run_prop_func):
        """
        Tests that parse_property function works expectedly with 0, 1 and 2 prop_funcs
        """
        prop_dict_1 = {'prop_name_1': 'prop_func_1'}
        prop_dict_2 = {'prop_name_1': 'prop_func_1', 'prop_name_2': 'prop_func_2'}

        item = 'example-openstack-resource'

        # 0 items
        assert not self.instance._parse_property(item, {})

        # 1 item
        _ = self.instance._parse_property(item, prop_dict_1)
        mock_run_prop_func.assert_called_once_with(
            item,
            'prop_func_1',
            default_out="Not Found"
        )

        # 2 items
        _ = self.instance._parse_property(item, prop_dict_2)
        mock_run_prop_func.assert_has_calls([
            call('example-openstack-resource', 'prop_func_1', default_out="Not Found"),
            call('example-openstack-resource', 'prop_func_2', default_out="Not Found")
        ])

    def test_run_prop_func_valid(self):
        """
        Test that run_prop_func function works expectedly with valid prop_func
        """
        item = 'some-openstack-resource'
        prop_func = MagicMock()
        prop_func.return_value = 'some_property_value'
        res = self.instance._run_prop_func(item, prop_func)

        prop_func.assert_called_once_with(item)
        self.assertEqual(res, prop_func.return_value)

    def test_run_prop_func_invalid(self):
        """
        Test that run_prop_func function works expectedly when prop_func raises an Attribute Error
        found for that object
        """
        item = 'some-openstack-resource'
        prop_func = MagicMock()
        prop_func.side_effect = AttributeError("some error here")
        res = self.instance._run_prop_func(item, prop_func, default_out='default_val')
        self.assertEqual(res, 'default_val')

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
        expected_resource_objects = ['obj1', 'obj2', 'obj3']
        expected_results = ['res1', 'res2', 'res3']

        self.instance._results_resource_objects = ['obj1', 'obj2', 'obj3']
        self.instance._results = ['res1', 'res2', 'res3']

        # with as_object false
        res = self.instance.to_list(as_objects=False)
        self.assertEqual(res, expected_results)

        # with as_object true
        res = self.instance.to_list(as_objects=True)
        self.assertEqual(res, expected_resource_objects)

    @patch("openstack_query.query_wrapper.QueryWrapper._generate_table")
    def test_to_html(self, mock_generate_table):
        """
        Tests that to_html function returns correct value
        """
        mocked_results = 'some_result'
        expected_out = 'some_output_string'
        mock_generate_table.return_value = 'some_output_string'

        self.instance._results = mocked_results
        res = self.instance.to_html()

        mock_generate_table.assert_called_once_with(
            mocked_results,
            return_html=True
        )

        self.assertEqual(expected_out, res)

    @patch("openstack_query.query_wrapper.QueryWrapper._generate_table")
    def test_to_string(self, mock_generate_table):
        """
        Tests that to_string function returns correct value
        """
        """
        Tests that to_html function returns correct value
        """
        mocked_results = 'some_result'
        expected_out = 'some_output_string'
        mock_generate_table.return_value = 'some_output_string'

        self.instance._results = mocked_results
        res = self.instance.to_string()

        mock_generate_table.assert_called_once_with(
            mocked_results,
            return_html=False
        )

        self.assertEqual(expected_out, res)

    @patch("openstack_query.query_wrapper.tabulate")
    def test_generate_table(self, mock_tabulate):
        results_dict_1 = [
            {'prop1': 'val1'},
            {'prop1': 'val2'}
        ]

        results_dict_2 = [
            {'prop1': 'val1', 'prop2': 'val2'}
        ]

        _ = self.instance._generate_table(results_dict_1, return_html=False)

        _ = self.instance._generate_table(results_dict_2, return_html=True)

        mock_tabulate.assert_has_calls([
            call([['val1'], ['val2']], ['prop1'], tablefmt='grid'),
            call([['val1', 'val2']], ['prop1', 'prop2'], tablefmt='html')
        ])

    @patch("openstack_query.query_wrapper.QueryWrapper._DEFAULT_FILTER_FUNCTION_MAPPINGS")
    @patch("openstack_query.query_wrapper.QueryWrapper._NON_DEFAULT_FILTER_FUNCTION_MAPPINGS")
    @patch("openstack_query.query_wrapper.QueryWrapper._get_default_filter_func")
    def test_get_filter_func(self, mock_get_default_ffn, mock_non_def_ffn_map, mock_def_ffn_map):

        # check when non def ffn has entry
        mock_non_def_ffn_map.keys.return_value = [QueryPresets.EQUAL_TO]
        mock_non_def_ffn_map.__getitem__.return_value = {MockedEnum.ITEM_2: 'ffn_1', MockedEnum.ITEM_3:'ffn_2'}
        mock_get_default_ffn.return_value = 'def_ffn'

        res = self.instance._get_filter_func(QueryPresets.EQUAL_TO, MockedEnum.ITEM_2)
        self.assertEqual(res, 'ffn_1')

        # check when def ffn has entry
        mock_def_ffn_map.keys.return_value = [QueryPresets.ANY_IN]
        mock_def_ffn_map.__getitem__.return_value = [MockedEnum.ITEM_4]
        res = self.instance._get_filter_func(QueryPresets.ANY_IN, MockedEnum.ITEM_4)
        self.assertEqual(res, 'def_ffn')

        # check when def ffn has entry '*'
        mock_def_ffn_map.keys.return_value = [QueryPresets.NOT_ANY_IN]
        mock_def_ffn_map.__getitem__.return_value = ['*']
        res = self.instance._get_filter_func(QueryPresets.NOT_ANY_IN, MockedEnum.ITEM_1)
        self.assertEqual(res, 'def_ffn')

        mock_get_default_ffn.has_calls([
            # second check
            call(QueryPresets.ANY_IN),
            call(QueryPresets.NOT_ANY_IN)
        ])

    @patch("openstack_query.query_wrapper.QueryWrapper._DEFAULT_FILTER_FUNCTIONS")
    def test_get_default_filter_func(self, mock_def_filter_funcs):
        mock_def_filter_funcs.get.return_value = 'some_filter_func'
        res = self.instance._get_default_filter_func(QueryPresets.EQUAL_TO)

        mock_def_filter_funcs.get.assert_called_once_with(QueryPresets.EQUAL_TO, None)
        self.assertEqual(res, 'some_filter_func')
