import unittest
from structs.query.query_output_details import QueryOutputDetails
from enums.query.props.server_properties import ServerProperties
from enums.query.query_output_types import QueryOutputTypes


class QueryOutputDetailsTests(unittest.TestCase):
    """
    This class tests that helper functions in the QueryOutputDetails
    """

    def setUp(self) -> None:
        self.instance = QueryOutputDetails

    def _run_from_kwargs_case(self, kwargs):
        """
        Helper function for running from_kwargs test cases
        """
        return self.instance.from_kwargs(prop_cls=ServerProperties, **kwargs)

    def test_from_kwargs_none_given(self):
        """
        tests that from_kwargs static method works expectedly - no kwargs given
        method should create a QueryOutputDetails with default params
        """
        res = self._run_from_kwargs_case({})
        self.assertEqual(res.properties_to_select, list(ServerProperties))
        self.assertEqual(res.output_type, QueryOutputTypes.TO_STR)
        self.assertEqual(res.group_by, None)
        self.assertEqual(res.sort_by, None)
        self.assertEqual(res.group_ranges, None)
        self.assertEqual(res.include_ungrouped_results, False)

    def test_from_kwargs_props_given(self):
        """
        tests that from_kwargs static method works expectedly - props given
        method should create a QueryOutputDetails with props set
        """
        res = self._run_from_kwargs_case(
            {"properties_to_select": ["server_id", "server_name"]}
        )
        self.assertEqual(
            res.properties_to_select,
            [ServerProperties.SERVER_ID, ServerProperties.SERVER_NAME],
        )

    def test_from_kwargs_output_type_given(self):
        """
        tests that from_kwargs static method works expectedly - output type given
        method should create a QueryOutputDetails with output type set
        """
        res = self._run_from_kwargs_case({"output_type": "TO_LIST"})
        self.assertEqual(res.output_type, QueryOutputTypes.TO_LIST)

    def test_from_kwargs_group_by_given(self):
        """
        tests that from_kwargs static method works expectedly - group by given
        method should create a QueryOutputDetails with group by set
        """
        res = self._run_from_kwargs_case({"group_by": "server_name"})
        self.assertEqual(res.group_by, ServerProperties.SERVER_NAME)

    def test_from_kwargs_sort_by_given(self):
        """
        tests that from_kwargs static method works expectedly - sort by given
        method should create a QueryOutputDetails with sort by set
        """
        res = self._run_from_kwargs_case({"sort_by": ["server_name", "server_id"]})
        self.assertEqual(
            res.sort_by,
            [
                (ServerProperties.SERVER_NAME, False),
                (ServerProperties.SERVER_ID, False),
            ],
        )
