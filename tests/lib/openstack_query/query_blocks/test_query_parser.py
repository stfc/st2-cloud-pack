import unittest
from unittest.mock import MagicMock, call, patch
from parameterized import parameterized

from openstack_query.query_blocks.query_parser import QueryParser
from nose.tools import raises

from exceptions.parse_query_error import ParseQueryError
from enums.query.props.server_properties import ServerProperties
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

# pylint:disable=protected-access


class QueryParserTests(unittest.TestCase):
    """
    Runs various tests to ensure that QueryParser class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        self.mock_get_cls = MockProperties
        self.instance = QueryParser(self.mock_get_cls)

    def _get_prop_func(self, prop):
        return MagicMock(wraps=lambda obj: self._prop_func(obj, prop))

    @staticmethod
    def _prop_func(obj, prop):
        """
        mock a property func assuming the property function was to get a property corresponding to 'prop_1'
        """
        return obj[prop.name.lower()]

    def test_group_by_prop(self):
        """
        Tests that property getter function group_by_prop gets the hidden attribute QueryParser._group_by
        """
        self.instance._group_by = "prop1"
        self.assertEqual(self.instance.group_by_prop, "prop1")

    def test_parse_sort_by_one_key(self):
        """
        Tests parse_sort_by method works expectedly - one sort-by key
        should call check_prop_valid and add it to sort_by attribute
        """
        self.instance._prop_enum_cls = MockProperties
        self.instance.parse_sort_by((MockProperties.PROP_1, False))
        self.assertEqual(dict(self.instance._sort_by), {MockProperties.PROP_1: False})

    def test_parse_sort_by_many_keys(self):
        """
        Tests parse_sort_by method works expectedly - two sort-by keys
        should call check_prop_valid and add it to sort_by attribute
        """
        self.instance._prop_enum_cls = MockProperties
        self.instance.parse_sort_by(
            (MockProperties.PROP_1, False), (MockProperties.PROP_2, True)
        )
        self.assertEqual(
            dict(self.instance._sort_by),
            {MockProperties.PROP_1: False, MockProperties.PROP_2: True},
        )

    @raises(ParseQueryError)
    def test_parse_sort_by_invalid(self):
        self.instance.parse_sort_by((ServerProperties.SERVER_ID, True))

    def test_parse_group_by_no_ranges(self):
        """
        Tests parse_group_by functions expectedly - with no ranges
        Should simply set the group_by property as prop given
        """
        self.instance.parse_group_by(MockProperties.PROP_1)
        self.assertEqual(self.instance._group_by, MockProperties.PROP_1)

    @patch("openstack_query.query_blocks.query_parser.QueryParser._parse_group_ranges")
    def test_parse_group_by_with_group_ranges(self, mock_parse_group_ranges):
        """
        Tests parse_group_by functions expectedly - with group ranges
        Should set group_by and call parse_group_ranges
        """
        mock_group_ranges = {"group1": ["val1", "val2", "val3"], "group2": ["val4"]}
        self.instance.parse_group_by(MockProperties.PROP_1, mock_group_ranges)
        self.assertEqual(self.instance._group_by, MockProperties.PROP_1)
        mock_parse_group_ranges.assert_called_once_with(mock_group_ranges)

    @patch("openstack_query.query_blocks.query_parser.QueryParser._parse_group_ranges")
    @patch(
        "openstack_query.query_blocks.query_parser.QueryParser._add_include_missing_group"
    )
    def test_parse_group_by_with_group_ranges_and_include_missing(
        self, mock_add_include_missing_group, mock_parse_group_ranges
    ):
        """
        Tests parse_group_by functions expectedly - with group ranges
        Should set group_by and call parse_group_ranges
        """
        mock_group_ranges = {"group1": ["val1", "val2", "val3"], "group2": ["val4"]}
        self.instance.parse_group_by(
            MockProperties.PROP_1, mock_group_ranges, include_missing=True
        )
        self.assertEqual(self.instance._group_by, MockProperties.PROP_1)
        mock_parse_group_ranges.assert_called_once_with(mock_group_ranges)
        mock_add_include_missing_group.assert_called_once_with(mock_group_ranges)

    def test_run_parse_group_ranges(self):
        """
        Tests parse_group_ranges functions expectedly
        Should setup groups based on given group mappings
        """
        mock_group_by = MockProperties.PROP_1
        self.instance._group_by = mock_group_by
        mock_group_ranges = {"group1": ["val1", "val2", "val3"], "group2": ["val4"]}

        with patch.object(
            MockProperties, "get_prop_mapping", wraps=self._get_prop_func
        ) as mock_get_prop_func:
            self.instance._parse_group_ranges(group_ranges=mock_group_ranges)
            mock_get_prop_func.assert_called_once_with(mock_group_by)

        self.assertTrue(self.instance._group_mappings["group1"]({"prop_1": "val1"}))
        self.assertFalse(self.instance._group_mappings["group2"]({"prop_1": "val1"}))

    def test_add_include_missing_group(self):
        mock_group_by = MockProperties.PROP_1
        self.instance._group_by = mock_group_by
        mock_group_ranges = {"group1": ["val1", "val2", "val3"], "group2": ["val4"]}

        with patch.object(
            MockProperties, "get_prop_mapping", wraps=self._get_prop_func
        ) as mock_get_prop_func:
            self.instance._add_include_missing_group(mock_group_ranges)
            mock_get_prop_func.assert_called_once_with(mock_group_by)

        self.assertTrue(
            self.instance._group_mappings["ungrouped results"]({"prop_1": "val5"})
        )
        self.assertFalse(
            self.instance._group_mappings["ungrouped results"]({"prop_1": "val1"})
        )
        self.assertFalse(
            self.instance._group_mappings["ungrouped results"]({"prop_1": "val4"})
        )

    @patch("openstack_query.query_blocks.query_parser.QueryParser._run_sort")
    def test_run_parser_with_sort_by(self, mock_run_sort):
        """
        Tests that run_parser functions expectedly - when giving only sort_by
        Should call run_sort method, and return result
        """
        self.instance._sort_by = {MockProperties.PROP_1: False}
        self.instance._group_by = None
        self.instance._group_mappings = {}

        mock_run_sort.return_value = "sort-out"
        mock_obj_list = ["obj1", "obj2", "obj3"]
        res = self.instance.run_parser(mock_obj_list)

        self.assertEqual(res, "sort-out")
        mock_run_sort.assert_called_once_with(mock_obj_list)

    @patch("openstack_query.query_blocks.query_parser.QueryParser._run_group_by")
    def test_run_parser_no_sort_with_group_mappings(self, mock_run_group_by):
        """
        Tests that run_parser functions expectedly - when giving group_mappings
        Should call run_group_by with group mappings and return
        """
        self.instance._sort_by = {}
        self.instance._group_by = MockProperties.PROP_1
        self.instance._group_mappings = {"group1": "some-mapping_func"}

        mock_obj_list = ["obj1", "obj2", "obj3"]
        mock_run_group_by.return_value = "group-out"
        self.instance._group_by = MockProperties.PROP_1

        res = self.instance.run_parser(mock_obj_list)
        self.assertEqual(res, "group-out")
        mock_run_group_by.assert_called_once_with(mock_obj_list)

    @patch("openstack_query.query_blocks.query_parser.QueryParser._run_sort")
    @patch("openstack_query.query_blocks.query_parser.QueryParser._run_group_by")
    def test_run_parser_with_sort_and_group(self, mock_run_group_by, mock_run_sort):
        """
        Tests that run_parser functions expectedly - when giving both group_by and sort_by
        Should call run_sort method and then run_group_by on that output, then return
        """
        self.instance._sort_by = {MockProperties.PROP_1: False}
        self.instance._group_by = MockProperties.PROP_1
        self.instance._group_mappings = {"group1": "some-mapping_func"}
        mock_obj_list = ["obj1", "obj2", "obj3"]

        mock_run_group_by.return_value = "group-out"
        mock_run_sort.return_value = "sort-out"

        res = self.instance.run_parser(mock_obj_list)
        self.assertEqual(res, "group-out")
        mock_run_sort.assert_called_once_with(mock_obj_list)
        mock_run_group_by.assert_called_once_with("sort-out")

    def _run_sort_by_tests(self, obj_list, sort_by_specs, expected_list):
        self.instance._sort_by = sort_by_specs
        with patch.object(
            MockProperties, "get_prop_mapping", wraps=self._get_prop_func
        ) as mock_get_prop_func:
            res = self.instance._run_sort(obj_list)
            self.assertEqual(res, expected_list)
            mock_get_prop_func.assert_has_calls(
                [call(sort_key) for sort_key in reversed(sort_by_specs.keys())]
            )

    @parameterized.expand(
        [
            (
                "string key ascending",
                {MockProperties.PROP_1: False},
            ),
            (
                "string key descending",
                {MockProperties.PROP_1: True},
            ),
            (
                "integer key ascending",
                {MockProperties.PROP_2: False},
            ),
            (
                "integer key descending",
                {MockProperties.PROP_2: True},
            ),
        ]
    )
    def test_run_sort_with_one_key(self, _, mock_sort_by_specs):
        """
        Tests that run_sort functions expectedly - with one sorting key
        Should call run_sort method which should get the appropriate sorting
        key lambda function and sort dict accordingly
        """

        mock_obj_list = [
            {"prop_1": "a", "prop_2": 2},
            {"prop_1": "c", "prop_2": 4},
            {"prop_1": "d", "prop_2": 3},
            {"prop_1": "b", "prop_2": 1},
        ]

        # sorting by only one property so get first key in sort specs
        mock_enum = list(mock_sort_by_specs.keys())[0]
        reverse = mock_sort_by_specs[mock_enum]
        mock_prop_name = mock_enum.name.lower()
        expected_list = sorted(
            mock_obj_list, key=lambda k: k[mock_prop_name], reverse=reverse
        )
        self._run_sort_by_tests(mock_obj_list, mock_sort_by_specs, expected_list)

    @parameterized.expand(
        [
            (
                "string key ascending, then age descending",
                {MockProperties.PROP_1: False, MockProperties.PROP_2: True},
                [
                    {"prop_1": "a", "prop_2": 2},
                    {"prop_1": "a", "prop_2": 1},
                    {"prop_1": "b", "prop_2": 2},
                    {"prop_1": "b", "prop_2": 1},
                ],
            ),
            (
                "string key descending, then age ascending",
                {MockProperties.PROP_1: True, MockProperties.PROP_2: False},
                [
                    {"prop_1": "b", "prop_2": 1},
                    {"prop_1": "b", "prop_2": 2},
                    {"prop_1": "a", "prop_2": 1},
                    {"prop_1": "a", "prop_2": 2},
                ],
            ),
            (
                "age key ascending, then string descending",
                {MockProperties.PROP_2: False, MockProperties.PROP_1: True},
                [
                    {"prop_1": "b", "prop_2": 1},
                    {"prop_1": "a", "prop_2": 1},
                    {"prop_1": "b", "prop_2": 2},
                    {"prop_1": "a", "prop_2": 2},
                ],
            ),
            (
                "age key descending, then string ascending",
                {MockProperties.PROP_2: True, MockProperties.PROP_1: False},
                [
                    {"prop_1": "a", "prop_2": 2},
                    {"prop_1": "b", "prop_2": 2},
                    {"prop_1": "a", "prop_2": 1},
                    {"prop_1": "b", "prop_2": 1},
                ],
            ),
        ]
    )
    def test_run_sort_with_multiple_key(self, _, mock_sort_by_specs, expected_list):
        """
        Tests that run_sort functions expectedly - with one sorting key
        Should call run_sort method which should get the appropriate sorting
        key lambda function and sort dict accordingly
        """

        mock_obj_list = [
            {"prop_1": "a", "prop_2": 1},
            {"prop_1": "b", "prop_2": 1},
            {"prop_1": "a", "prop_2": 2},
            {"prop_1": "b", "prop_2": 2},
        ]
        self._run_sort_by_tests(mock_obj_list, mock_sort_by_specs, expected_list)

    @parameterized.expand(
        [
            (
                "boolean ascending",
                {MockProperties.PROP_1: False},
            ),
            (
                "boolean ascending",
                {MockProperties.PROP_1: True},
            ),
        ]
    )
    def test_run_sort_with_boolean(self, _, mock_sort_by_specs):
        """
        Tests that run_sort functions expectedly - sorting by boolean
        Should call run_sort method which should get the appropriate sorting
        key lambda function and sort dict accordingly
        """
        mock_obj_list = [
            {"prop_1": False},
            {"prop_1": True},
        ]
        self.instance._sort_by = mock_sort_by_specs
        mock_enum = list(mock_sort_by_specs.keys())[0]
        reverse = mock_sort_by_specs[mock_enum]
        mock_prop_name = mock_enum.name.lower()

        expected_list = sorted(
            mock_obj_list, key=lambda k: k[mock_prop_name], reverse=reverse
        )
        self._run_sort_by_tests(mock_obj_list, mock_sort_by_specs, expected_list)

    @parameterized.expand(
        [
            (
                "group by prop_1",
                MockProperties.PROP_1,
                {
                    "a": [
                        {"prop_1": "a", "prop_2": 1},
                        {"prop_1": "a", "prop_2": 3},
                    ],
                    "b": [{"prop_1": "b", "prop_2": 2}],
                },
            ),
            (
                "group by prop_2",
                MockProperties.PROP_2,
                {
                    1: [{"prop_1": "a", "prop_2": 1}],
                    2: [{"prop_1": "b", "prop_2": 2}],
                    3: [{"prop_1": "a", "prop_2": 3}],
                },
            ),
        ]
    )
    def test_build_unique_val_groups(self, _, mock_group_by, expected_out):
        """
        Tests that build_unique_val_groups method functions expectedly
        method should find all unique values for a test object list for a given property and create appropriate
        group_ranges to be used for group-by
        """

        obj_list = [
            {"prop_1": "a", "prop_2": 1},
            {"prop_1": "b", "prop_2": 2},
            {"prop_1": "a", "prop_2": 3},
        ]
        self.instance._group_by = mock_group_by

        with patch.object(
            MockProperties, "get_prop_mapping", wraps=self._get_prop_func
        ) as mock_get_prop_func:
            res = self.instance._build_unique_val_groups(obj_list)
            self.assertEqual(res.keys(), expected_out.keys())
            mock_get_prop_func.assert_called_once_with(mock_group_by)

        # now that we have the group mappings - check that using them produces expected results
        grouped_out = {
            name: [item for item in obj_list if map_func(item)]
            for name, map_func in res.items()
        }
        self.assertEqual(grouped_out, expected_out)

    @patch(
        "openstack_query.query_blocks.query_parser.QueryParser._build_unique_val_groups"
    )
    def test_run_group_by_no_group_mappings(self, mock_build_unique_val_groups):
        """
        Tests run group_by method functions expectedly - when using no group mappings
        Should call build_unique_val_group and use the mappings returned to apply onto given object list
        """
        self.instance._group_mappings = {}
        self.instance._group_by = MockProperties.PROP_1

        mock_group_mappings = {
            "group1": lambda obj: obj["prop_1"] == "a",
            "group2": lambda obj: obj["prop_1"] == "b",
            "group3": lambda obj: obj["prop_1"] == "c",
        }
        mock_build_unique_val_groups.return_value = mock_group_mappings

        mock_obj_list = [
            {"prop_1": "a", "prop_2": 1},
            {"prop_1": "b", "prop_2": 2},
            {"prop_1": "c", "prop_2": 3},
        ]

        res = self.instance._run_group_by(mock_obj_list)
        mock_build_unique_val_groups.assert_called_once_with(mock_obj_list)

        self.assertEqual(
            res,
            {
                "group1": [{"prop_1": "a", "prop_2": 1}],
                "group2": [{"prop_1": "b", "prop_2": 2}],
                "group3": [{"prop_1": "c", "prop_2": 3}],
            },
        )

    @patch(
        "openstack_query.query_blocks.query_parser.QueryParser._build_unique_val_groups"
    )
    def test_run_group_by_with_group_mappings(self, mock_build_unique_val_groups):
        """
        Tests run group_by method functions expectedly - when using group mappings
        Should use the preset mappings and apply them onto given object list
        """
        self.instance._group_by = MockProperties.PROP_1

        mock_group_mappings = {
            "group1": lambda obj: obj["prop_2"] in [1, 2],
            "group2": lambda obj: obj["prop_2"] in [3],
        }
        self.instance._group_mappings = mock_group_mappings

        mock_obj_list = [
            {"prop_1": "a", "prop_2": 1},
            {"prop_1": "b", "prop_2": 2},
            {"prop_1": "c", "prop_2": 3},
        ]

        res = self.instance._run_group_by(mock_obj_list)
        mock_build_unique_val_groups.assert_not_called()

        self.assertEqual(
            res,
            {
                "group1": [{"prop_1": "a", "prop_2": 1}, {"prop_1": "b", "prop_2": 2}],
                "group2": [{"prop_1": "c", "prop_2": 3}],
            },
        )
