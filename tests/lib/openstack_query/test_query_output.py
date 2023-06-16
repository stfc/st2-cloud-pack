import unittest
from unittest.mock import MagicMock, patch, call
from openstack_query.query_output import QueryOutput

from tests.lib.openstack_query.mocks.mocked_props import MockProperties
from exceptions.query_property_mapping_error import QueryPropertyMappingError


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

    @patch("openstack_query.query_output.QueryOutput._generate_table")
    def test_to_html(self, mock_generate_table):
        """
        Tests that to_html function returns correct value
        """
        mocked_results = "some_result"
        expected_out = "some_output_string"
        mock_generate_table.return_value = "some_output_string"

        self.instance._results = mocked_results
        res = self.instance.to_html()

        mock_generate_table.assert_called_once_with(mocked_results, return_html=True)

        self.assertEqual(expected_out, res)

    @patch("openstack_query.query_output.QueryOutput._generate_table")
    def test_to_string(self, mock_generate_table):
        """
        Tests that to_string function returns correct value
        """
        """
        Tests that to_html function returns correct value
        """
        mocked_results = "some_result"
        expected_out = "some_output_string"
        mock_generate_table.return_value = "some_output_string"

        self.instance._results = mocked_results
        res = self.instance.to_string()

        mock_generate_table.assert_called_once_with(mocked_results, return_html=False)

        self.assertEqual(expected_out, res)

    @patch("openstack_query.query_output.tabulate")
    def test_generate_table(self, mock_tabulate):
        results_dict_1 = [{"prop1": "val1"}, {"prop1": "val2"}]

        results_dict_2 = [{"prop1": "val1", "prop2": "val2"}]

        _ = self.instance._generate_table(results_dict_1, return_html=False)

        _ = self.instance._generate_table(results_dict_2, return_html=True)

        mock_tabulate.assert_has_calls(
            [
                call([["val1"], ["val2"]], ["prop1"], tablefmt="grid"),
                call([["val1", "val2"]], ["prop1", "prop2"], tablefmt="html"),
            ]
        )

    def test_parse_select_with_select_all(self):
        # if select_all flag set, get all props
        self.mock_prop_handler.all_props.return_value = ["prop1", "prop2"]
        self.instance.parse_select(select_all=True)
        self.assertEqual(self.instance._props, {"prop1", "prop2"})

    @patch("openstack_query.query_output.QueryOutput._check_prop_valid")
    def test_parse_select_given_args(self, mock_check_prop_valid):
        # if given props
        mock_check_prop_valid.return_value = True
        self.instance.parse_select("prop3", "prop4")
        mock_check_prop_valid.assert_has_calls([call("prop3"), call("prop4")])
        self.assertEqual(self.instance._props, {"prop3", "prop4"})

    def test_check_prop_valid(self):
        """
        Tests that check_prop_valid works expectedly
        """

        # when prop_handler exists
        self.mock_prop_handler.check_supported.return_value = True
        self.assertTrue(self.instance._check_prop_valid(MockProperties.PROP_1))

        # when prop_handler not found
        self.mock_prop_handler.check_supported.return_value = False
        with self.assertRaises(QueryPropertyMappingError):
            self.instance._check_prop_valid(MockProperties.PROP_1)

    @patch("openstack_query.query_output.QueryOutput._parse_property")
    def test_generate_output(self, mock_parse_property):
        """
        Tests that parse_properties function works expectedly with 0, 1 and 2 items
        """
        item_1 = "openstack-resource-1"
        item_2 = "openstack-resource-2"
        self.mock_prop_handler.get_prop.return_value = ["prop-func1", "prop-func2"]
        # 1 item
        _ = self.instance.generate_output([item_1])
        mock_parse_property.assert_called_once_with(item_1)

        # 2 items
        mock_parse_property.reset_mock()
        _ = self.instance.generate_output([item_1, item_2])
        mock_parse_property.assert_has_calls(
            [call("openstack-resource-1"), call("openstack-resource-2")]
        )

    def test_parse_property(self):
        """
        Tests that parse_property function works expectedly with 0, 1 and 2 prop_funcs
        """

        # 0 items
        self.instance._props = set()
        self.assertEqual(self.instance._parse_property("openstack-item"), {})

        # 1 item
        self.instance._props = {MockProperties.PROP_1}
        self.mock_prop_handler.get_prop.return_value = "prop1-func"
        res = self.instance._parse_property("openstack-item")
        self.assertEqual(res, {"prop_1": "prop1-func"})

        # 2 items
        self.mock_prop_handler.reset_mock()
        self.instance._props = {MockProperties.PROP_1, MockProperties.PROP_2}
        self.mock_prop_handler.get_prop.side_effect = ["prop1-func", "prop2-func"]
        res = self.instance._parse_property("openstack-item")
        self.assertEqual(res, {"prop_1": "prop1-func", "prop_2": "prop2-func"})
