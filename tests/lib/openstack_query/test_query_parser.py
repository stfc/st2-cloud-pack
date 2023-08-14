import unittest
from unittest.mock import MagicMock, call, patch
from nose.tools import raises
from parameterized import parameterized

from openstack_query.query_parser import QueryParser
from exceptions.parse_query_error import ParseQueryError
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
        self.mock_prop_handler = MagicMock()
        self.mock_prop_handler.get_prop = MagicMock(wraps=self.mock_get_prop)
        self.instance = QueryParser(self.mock_prop_handler)

    @staticmethod
    def mock_get_prop(obj, prop):
        """simply return obj as prop value to compare"""
        return obj[prop]

    @patch("openstack_query.query_parser.QueryParser._check_prop_valid")
    def test_parse_sort_by_one_key(self, mock_check_prop_valid):
        """
        Tests parse_sort_by method works expectedly - one sort-by key
        should call check_prop_valid and add it to sort_by attribute
        """
        self.instance.parse_sort_by((MockProperties.PROP_1, False))
        self.assertEqual(dict(self.instance._sort_by), {MockProperties.PROP_1: False})
        mock_check_prop_valid.assert_called_once_with(MockProperties.PROP_1)

    @patch("openstack_query.query_parser.QueryParser._check_prop_valid")
    def test_parse_sort_by_many_keys(self, mock_check_prop_valid):
        """
        Tests parse_sort_by method works expectedly - two sort-by keys
        should call check_prop_valid and add it to sort_by attribute
        """
        self.instance.parse_sort_by(
            (MockProperties.PROP_1, False), (MockProperties.PROP_2, True)
        )
        self.assertEqual(
            dict(self.instance._sort_by),
            {MockProperties.PROP_1: False, MockProperties.PROP_2: True},
        )
        mock_check_prop_valid.assert_has_calls(
            [call(MockProperties.PROP_1), call(MockProperties.PROP_2)]
        )

    @parameterized.expand(
        [("no include missing", False), ("with include missing", True)]
    )
    @patch("openstack_query.query_parser.QueryParser._check_prop_valid")
    def test_parse_group_by_with_group_ranges(
        self, _, include_missing, mock_check_prop_valid
    ):
        """
        Tests parse_group_by method works expectedly - with valid group ranges defined
        should create a dictionary with group names mapped to lambda functions
            - which return True or False if a given resource false into group
        """

        mock_group_ranges = {"group1": ["val1", "val2", "val3"], "group2": ["val4"]}

        self.instance.parse_group_by(
            group_by="prop1",
            group_ranges=mock_group_ranges,
            include_missing=include_missing,
        )

        mock_check_prop_valid.assert_called_once_with("prop1")
        if not include_missing:
            self.assertEqual(
                self.instance._group_mappings.keys(), mock_group_ranges.keys()
            )
        else:
            self.assertEqual(
                list(self.instance._group_mappings.keys()),
                (list(mock_group_ranges.keys()) + ["ungrouped results"]),
            )

        # test that group_mappings contain a callable lambda that uses _get_prop() func
        self.assertTrue(self.instance._group_mappings["group1"]({"prop1": "val1"}))
        self.assertFalse(self.instance._group_mappings["group2"]({"prop1": "val1"}))

        self.mock_prop_handler.get_prop.assert_has_calls(
            [call({"prop1": "val1"}, "prop1"), call({"prop1": "val1"}, "prop1")]
        )

        # test that include_missing group contains callable lambda
        if include_missing:
            self.assertTrue(
                self.instance._group_mappings["ungrouped results"]({"prop1": "val5"})
            )
            self.assertFalse(
                self.instance._group_mappings["ungrouped results"]({"prop1": "val1"})
            )

    @patch("openstack_query.query_parser.QueryParser._check_prop_valid")
    def test_parse_group_by_no_ranges(self, mock_check_prop_valid):
        """
        Tests parse_group_by functions expectedly - with no ranges
        Should simply set the group_by property as prop given
        """
        self.instance.parse_group_by(MockProperties.PROP_1)
        mock_check_prop_valid.assert_called_once_with(MockProperties.PROP_1)
        self.assertEqual(self.instance._group_by, MockProperties.PROP_1)

    @patch("openstack_query.query_parser.QueryParser._run_sort")
    def test_run_parser_with_sort_by(self, mock_run_sort):
        """
        Tests that run_parser functions expectedly - when giving only sort_by
        Should call run_sort method, and return result
        """
        self.instance._sort_by = (MockProperties.PROP_1, False)
        mock_run_sort.return_value = "sort-out"
        mock_obj_list = ["obj1", "obj2", "obj3"]
        res = self.instance.run_parser(mock_obj_list)

        self.assertEqual(res, "sort-out")
        mock_run_sort.assert_called_once_with(mock_obj_list, self.instance._sort_by)

    @patch("openstack_query.query_parser.QueryParser._run_group_by")
    def test_run_parser_with_group_mappings(self, mock_run_group_by):
        """
        Tests that run_parser functions expectedly - when giving group_mappings
        Should call run_group_by with group mappings and return
        """
        self.instance._group_by = MockProperties.PROP_1
        self.instance._group_mappings = {"group1": "some-mapping_func"}
        mock_obj_list = ["obj1", "obj2", "obj3"]
        mock_run_group_by.return_value = "group-out"
        self.instance._group_by = MockProperties.PROP_1

        res = self.instance.run_parser(mock_obj_list)
        self.assertEqual(res, "group-out")
        mock_run_group_by.assert_called_once_with(
            mock_obj_list, self.instance._group_mappings
        )

    @patch("openstack_query.query_parser.QueryParser._build_unique_val_groups")
    @patch("openstack_query.query_parser.QueryParser._run_group_by")
    def test_run_parser_with_no_group_mappings(
        self, mock_run_group_by, mock_build_unique_val_groups
    ):
        """
        Tests that run_parser functions expectedly - when giving group_by with no group_mappings
        Should call build_unique_val_groups first to set group_mappings and then call run_group_by and return
        """
        self.instance._group_by = MockProperties.PROP_1
        mock_obj_list = ["obj1", "obj2", "obj3"]
        mock_build_unique_val_groups.return_value = "group-mapping-out"
        mock_run_group_by.return_value = "group-out"

        res = self.instance.run_parser(mock_obj_list)
        self.assertEqual(res, "group-out")
        mock_build_unique_val_groups.assert_called_once_with(
            mock_obj_list, group_by_prop=MockProperties.PROP_1
        )
        mock_run_group_by.assert_called_once_with(mock_obj_list, "group-mapping-out")

    @patch("openstack_query.query_parser.QueryParser._run_sort")
    @patch("openstack_query.query_parser.QueryParser._run_group_by")
    def test_run_parser_with_sort_and_group(self, mock_run_group_by, mock_run_sort):
        """
        Tests that run_parser functions expectedly - when giving both group_by and sort_by
        Should call run_sort method and then run_group_by on that output, then return
        """
        self.instance._sort_by = (MockProperties.PROP_1, False)
        self.instance._group_by = MockProperties.PROP_1
        self.instance._group_mappings = {"group1": "some-mapping_func"}
        mock_obj_list = ["obj1", "obj2", "obj3"]

        mock_run_group_by.return_value = "group-out"
        mock_run_sort.return_value = "sort-out"

        res = self.instance.run_parser(mock_obj_list)
        self.assertEqual(res, "group-out")
        mock_run_sort.assert_called_once_with(mock_obj_list, self.instance._sort_by)
        mock_run_group_by.assert_called_once_with(
            "sort-out", self.instance._group_mappings
        )

    @parameterized.expand(
        [
            (
                "string key ascending",
                {"arg1": False},
                [
                    {"arg1": "a", "arg2": 2},
                    {"arg1": "b", "arg2": 1},
                    {"arg1": "c", "arg2": 4},
                    {"arg1": "d", "arg2": 3},
                ],
            ),
            (
                "string key descending",
                {"arg1": True},
                [
                    {"arg1": "d", "arg2": 3},
                    {"arg1": "c", "arg2": 4},
                    {"arg1": "b", "arg2": 1},
                    {"arg1": "a", "arg2": 2},
                ],
            ),
            (
                "integer key ascending",
                {"arg2": False},
                [
                    {"arg1": "b", "arg2": 1},
                    {"arg1": "a", "arg2": 2},
                    {"arg1": "d", "arg2": 3},
                    {"arg1": "c", "arg2": 4},
                ],
            ),
            (
                "integer key descending",
                {"arg2": True},
                [
                    {"arg1": "c", "arg2": 4},
                    {"arg1": "d", "arg2": 3},
                    {"arg1": "a", "arg2": 2},
                    {"arg1": "b", "arg2": 1},
                ],
            ),
        ]
    )
    def test_run_sort_with_one_key(self, _, mock_sort_by_specs, expected_res):
        """
        Tests that run_sort functions expectedly - with one sorting key
        Should call run_sort method which should get the appropriate sorting
        key lambda function and sort dict accordingly
        """

        mock_obj_list = [
            {"arg1": "a", "arg2": 2},
            {"arg1": "c", "arg2": 4},
            {"arg1": "d", "arg2": 3},
            {"arg1": "b", "arg2": 1},
        ]

        res = self.instance._run_sort(mock_obj_list, sort_by_specs=mock_sort_by_specs)
        self.assertEqual(res, expected_res)

    @parameterized.expand(
        [
            (
                "string key ascending, then age descending",
                {"arg1": False, "arg2": True},
                [
                    {"arg1": "a", "arg2": 2},
                    {"arg1": "a", "arg2": 1},
                    {"arg1": "b", "arg2": 2},
                    {"arg1": "b", "arg2": 1},
                ],
            ),
            (
                "string key descending, then age ascending",
                {"arg1": True, "arg2": False},
                [
                    {"arg1": "b", "arg2": 1},
                    {"arg1": "b", "arg2": 2},
                    {"arg1": "a", "arg2": 1},
                    {"arg1": "a", "arg2": 2},
                ],
            ),
            (
                "age key ascending, then string descending",
                {"arg2": False, "arg1": True},
                [
                    {"arg1": "b", "arg2": 1},
                    {"arg1": "a", "arg2": 1},
                    {"arg1": "b", "arg2": 2},
                    {"arg1": "a", "arg2": 2},
                ],
            ),
            (
                "age key descending, then string ascending",
                {"arg2": True, "arg1": False},
                [
                    {"arg1": "a", "arg2": 2},
                    {"arg1": "b", "arg2": 2},
                    {"arg1": "a", "arg2": 1},
                    {"arg1": "b", "arg2": 1},
                ],
            ),
        ]
    )
    def test_run_sort_with_multiple_key(self, _, mock_sort_by_specs, expected_res):
        """
        Tests that run_sort functions expectedly - with one sorting key
        Should call run_sort method which should get the appropriate sorting
        key lambda function and sort dict accordingly
        """

        mock_obj_list = [
            {"arg1": "a", "arg2": 1},
            {"arg1": "b", "arg2": 1},
            {"arg1": "a", "arg2": 2},
            {"arg1": "b", "arg2": 2},
        ]

        res = self.instance._run_sort(mock_obj_list, sort_by_specs=mock_sort_by_specs)
        self.assertEqual(res, expected_res)

    @parameterized.expand(
        [
            (
                "boolean ascending",
                {"enabled": False},
                [
                    {"enabled": False},
                    {"enabled": True},
                ],
            ),
            (
                "boolean ascending",
                {"enabled": True},
                [
                    {"enabled": True},
                    {"enabled": False},
                ],
            ),
        ]
    )
    def test_run_sort_with_boolean(self, _, mock_sort_by_specs, expected_res):
        mock_obj_list = [
            {"enabled": False},
            {"enabled": True},
        ]

        res = self.instance._run_sort(mock_obj_list, sort_by_specs=mock_sort_by_specs)
        self.assertEqual(res, expected_res)

    @parameterized.expand(
        [
            ("group by arg1", "arg1", ["a", "b", "c"]),
            ("group by arg2", "arg2", [1, 2, 3]),
        ]
    )
    def test_build_unique_val_groups(self, _, mock_group_by_prop, expected_unique_vals):
        """
        Tests that build_unique_val_groups method functions expectedly
        method should find all unique values for a test object list for a given property and create appropriate
        group_ranges to be used for group-by
        """

        def mock_get_prop(obj, prop):
            return obj[prop.name]

        self.mock_prop_handler.get_prop = MagicMock(wraps=mock_get_prop)

        obj_list = [
            {"arg1": "a", "arg2": 1},
            {"arg1": "b", "arg2": 2},
            {"arg1": "c", "arg2": 3},
        ]
        mock_prop_enum = MagicMock()
        mock_prop_enum.name = mock_group_by_prop
        res = self.instance._build_unique_val_groups(
            obj_list,
            mock_prop_enum,
        )
        expected_group_names = [
            f"{mock_group_by_prop} with value {val}" for val in expected_unique_vals
        ]
        self.assertEqual(list(res.keys()), expected_group_names)

        # check that groups are unique
        for i, key in enumerate(res.keys()):
            for j, test_val in enumerate(expected_unique_vals):
                test_bool = res[key]({mock_group_by_prop: test_val})

                # if the function is run with prop matching expected val - should return True
                if i == j:
                    self.assertTrue(test_bool)

                # if the function is run with prop not matching expected val - should return False
                else:
                    self.assertFalse(test_bool)

    def test_run_group_by(self):
        mock_group_mappings = {
            "group1": lambda obj: obj["arg1"] == "a",
            "group2": lambda obj: obj["arg1"] in ["b", "c"],
        }

        mock_obj_list = [
            {"arg1": "a", "arg2": 1},
            {"arg1": "b", "arg2": 2},
            {"arg1": "c", "arg2": 3},
        ]

        res = self.instance._run_group_by(mock_obj_list, mock_group_mappings)
        self.assertEqual(
            res,
            {
                "group1": [{"arg1": "a", "arg2": 1}],
                "group2": [{"arg1": "b", "arg2": 2}, {"arg1": "c", "arg2": 3}],
            },
        )
