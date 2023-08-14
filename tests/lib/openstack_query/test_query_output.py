import unittest
from unittest.mock import MagicMock, patch, call
from parameterized import parameterized
from nose.tools import raises

from openstack_query.query_output import QueryOutput
from exceptions.query_property_mapping_error import QueryPropertyMappingError
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


class QueryOutputTests(unittest.TestCase):
    """
    Runs various tests to ensure that QueryOutput class methods function expectedly
    """

    def setUp(self) -> None:
        """
        Setup for tests
        """
        super().setUp()
        self.mock_prop_handler = MagicMock()
        self.instance = QueryOutput(self.mock_prop_handler)

    # pylint:disable=unused-argument
    def _mock_get_prop_func(self, item, prop, default_out):
        """
        mock _get_prop_func for prop_handler to return a mock prop value
        :param item: stub openstack resource item
        :param prop: Enum representing property
        :param default_out: stub for default output value
        :returns: '{prop.name}'-func
        """
        return f"{prop.name.lower()}-func"

    def test_selected_props(self):
        """
        Tests that property method to get selected props works expectedly
        method should return self._props as a list
        """
        self.instance._props = {"prop1", "prop2", "prop3"}
        res = self.instance.selected_props
        self.assertEqual(res, list({"prop1", "prop2", "prop3"}))

    @parameterized.expand([("no title", None), ("with title", "test title")])
    @patch("openstack_query.query_output.QueryOutput._generate_table")
    def test_to_html_with_grouped_results(self, _, mock_title, mock_generate_table):
        """
        Tests that to_html function works expectedly - when given grouped results
        method should call generate_table with return_html for each group
        """
        mocked_results = {"group1": ["obj1", "obj2"], "group2": ["obj3", "obj4"]}
        mock_generate_table.side_effect = ["1 out, ", "2 out"]

        self.instance._results = mocked_results
        res = self.instance.to_html(results=mocked_results, title=mock_title)
        mock_generate_table.assert_has_calls(
            [
                call(["obj1", "obj2"], return_html=True, title="<b> group1: </b><br/>"),
                call(["obj3", "obj4"], return_html=True, title="<b> group2: </b><br/>"),
            ]
        )

        expected_out = ""
        if mock_title:
            expected_out = f"<b> {mock_title} </b><br/>"
        expected_out += "1 out, 2 out"

        self.assertEqual(expected_out, res)

    @parameterized.expand([("no title", None), ("with title", "test title")])
    @patch("openstack_query.query_output.QueryOutput._generate_table")
    def test_to_html_with_list_results(self, _, mock_title, mock_generate_table):
        """
        Tests that to_html function works expectedly - when given list as results
        method should call generate_table with return_html once
        """
        mocked_results = ["obj1", "obj2"]
        mock_generate_table.return_value = "mock out"

        self.instance._results = mocked_results
        res = self.instance.to_html(results=mocked_results, title=mock_title)
        mock_generate_table.assert_called_once_with(
            mocked_results, return_html=True, title=None
        )

        expected_out = ""
        if mock_title:
            expected_out = f"<b> {mock_title} </b><br/>"
        expected_out += "mock out"

        self.assertEqual(expected_out, res)

    @parameterized.expand([("no title", None), ("with title", "test title")])
    @patch("openstack_query.query_output.QueryOutput._generate_table")
    def test_to_string_with_grouped_results(self, _, mock_title, mock_generate_table):
        """
        Tests that to_string function works expectedly - when given grouped results
        method should call generate_table with return_html set to false for each group
        """
        mocked_results = {"group1": ["obj1", "obj2"], "group2": ["obj3", "obj4"]}
        mock_generate_table.side_effect = ["1 out, ", "2 out"]

        self.instance._results = mocked_results
        self.instance.to_string(results=mocked_results, title=mock_title)
        mock_generate_table.assert_has_calls(
            [
                call(["obj1", "obj2"], return_html=False, title="group1:\n"),
                call(["obj3", "obj4"], return_html=False, title="group2:\n"),
            ]
        )

        expected_out = ""
        if mock_title:
            expected_out = f"{mock_title}:\n"
        expected_out += "1 out, 2 out"

    @parameterized.expand([("no title", None), ("with title", "test title")])
    @patch("openstack_query.query_output.QueryOutput._generate_table")
    def test_to_string_with_list_results(self, _, mock_title, mock_generate_table):
        """
        Tests that to_string function works expectedly - when given list as results
        method should call generate_table with return_html set to false once
        """
        mocked_results = ["obj1", "obj2"]
        mock_generate_table.return_value = "mock out"

        self.instance._results = mocked_results
        res = self.instance.to_string(results=mocked_results, title=mock_title)
        mock_generate_table.assert_called_once_with(
            mocked_results, return_html=False, title=None
        )

        expected_out = ""
        if mock_title:
            expected_out = f"{mock_title}:\n"
        expected_out += "mock out"

        self.assertEqual(expected_out, res)

    @parameterized.expand([("no title", None), ("with title", "test title")])
    @patch("openstack_query.query_output.tabulate")
    def test_generate_table_no_vals(self, _, mock_title, mock_tabulate):
        """
        Tests that generate_table function works expectedly - when results empty
        method should return No results found
        """
        results_dict_0 = []

        no_out = self.instance._generate_table(
            results_dict_0, title=mock_title, return_html=False
        )
        if mock_title:
            self.assertEqual(no_out, f"{mock_title}\nNo results found")
        else:
            self.assertEqual(no_out, "No results found")

    @parameterized.expand([("no title", None), ("with title", "test title")])
    @patch("openstack_query.query_output.tabulate")
    def test_generate_table_with_vals(self, _, mock_title, mock_tabulate):
        """
        Tests that generate_table function works expectedly - with results
        method should format results dict and call tabulate and return a string of the tabled results
        """

        results_dict_1 = [{"prop1": "val1"}, {"prop1": "val2"}]
        results_dict_2 = [{"prop1": "val1", "prop2": "val2"}]

        _ = self.instance._generate_table(results_dict_1, return_html=False, title=None)
        _ = self.instance._generate_table(results_dict_2, return_html=True, title=None)

        self.assertEqual(
            mock_tabulate.call_args_list,
            [
                call([["val1"], ["val2"]], ["prop1"], tablefmt="grid"),
                call([["val1", "val2"]], ["prop1", "prop2"], tablefmt="html"),
            ],
        )

    def test_parse_select_with_select_all(self):
        """
        tests that parse select works expectedly - when called from select_all() - no props given
        method should set props internal attribute to all available props supported by prop_handler
        """
        # if select_all flag set, get all props
        self.mock_prop_handler.all_props.return_value = ["prop1", "prop2"]
        self.instance.parse_select(select_all=True)
        self.assertEqual(self.instance._props, {"prop1", "prop2"})

    @patch("openstack_query.query_output.QueryOutput._check_prop_valid")
    def test_parse_select_given_args(self, mock_check_prop_valid):
        """
        tests that parse select works expectedly - when called from select() - where props args given
        method should set check each given prop to see if mapping exists in prop_handler and
        add to internal attribute set props
        """
        # if given props
        mock_check_prop_valid.return_value = True
        self.instance.parse_select("prop3", "prop4")
        mock_check_prop_valid.assert_has_calls([call("prop3"), call("prop4")])
        self.assertEqual(self.instance._props, {"prop3", "prop4"})

    def test_check_prop_valid(self):
        """
        Tests that check_prop_valid works expectedly
        method should return true when given a valid prop which is supported by prop_handler
        """

        # when prop_handler exists
        self.mock_prop_handler.check_supported.return_value = True
        self.instance._check_prop_valid(MockProperties.PROP_1)

    @raises(QueryPropertyMappingError)
    def test_check_prop_invalid(self):
        """
        Tests that check_prop_valid works expectedly
        method should raise error when given an invalid prop which is not supported by prop_handler
        """

        # when prop_handler not found
        self.mock_prop_handler.check_supported.return_value = False
        self.instance._check_prop_valid(MockProperties.PROP_1)

    def test_generate_output_no_items(self):
        """
        Tests that parse_properties function works expectedly - no openstack items
        method should return an empty list
        """
        self.mock_prop_handler.get_prop.return_value = ["prop-func1", "prop-func2"]
        self.assertEqual(self.instance.generate_output([]), [])

    @patch("openstack_query.query_output.QueryOutput._parse_property")
    def test_generate_output_one_item(self, mock_parse_property):
        """
        Tests that parse_properties function works expectedly - 1 item
        method should call parse_property with the singular item
        """
        item_1 = "openstack-resource-1"
        self.mock_prop_handler.get_prop.return_value = ["prop-func1", "prop-func2"]
        self.instance.generate_output([item_1])
        mock_parse_property.assert_called_once_with(item_1)

    @patch("openstack_query.query_output.QueryOutput._parse_property")
    def test_generate_output_multiple_items(self, mock_parse_property):
        """
        Tests that parse_properties function works expectedly - many items
        method should call parse_property multiple times with each item in item list
        """

        item_1 = "openstack-resource-1"
        item_2 = "openstack-resource-2"
        self.mock_prop_handler.get_prop.return_value = ["prop-func1", "prop-func2"]

        _ = self.instance.generate_output([item_1, item_2])
        mock_parse_property.assert_has_calls(
            [call("openstack-resource-1"), call("openstack-resource-2")]
        )

    def test_parse_property_no_props(self):
        """
        Tests that parse_property function works expectedly with 0 prop_funcs to apply
        method should return an empty dict
        """

        # mock get_prop_func to return a func string appropriate for that prop
        self.instance._props = set()
        self.assertEqual(self.instance._parse_property("openstack-item"), {})

    def test_parse_property_one_prop(self):
        """
        Tests that parse_property function works expectedly with 0 prop_funcs to apply
        method should return a dict with one key value pair (prop-name, prop-value)
        """

        self.mock_prop_handler.get_prop = self._mock_get_prop_func
        self.instance._props = {MockProperties.PROP_1}
        res = self.instance._parse_property("openstack-item")
        self.assertEqual(res, {"prop_1": "prop_1-func"})

    def test_parse_property_many_props(self):
        """
        Tests that parse_property function works expectedly with 0 prop_funcs to apply
        method should return a dict with many key value pairs (prop-name, prop-value)
        """
        self.mock_prop_handler.get_prop = self._mock_get_prop_func
        self.instance._props = {MockProperties.PROP_1, MockProperties.PROP_2}
        res = self.instance._parse_property("openstack-item")
        self.assertEqual(res, {"prop_1": "prop_1-func", "prop_2": "prop_2-func"})
