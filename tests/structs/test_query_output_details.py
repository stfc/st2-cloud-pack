import unittest
from parameterized import parameterized
from structs.query.query_output_details import QueryOutputDetails
from enums.query.props.server_properties import ServerProperties
from enums.query.query_output_types import QueryOutputTypes


class QueryOutputDetailsTests(unittest.TestCase):
    """
    This class tests that helper functions in the QueryOutputDetails
    """

    def setUp(self) -> None:
        self.instance = QueryOutputDetails

    @parameterized.expand(
        [
            ("none given", {}),
            ("props given", {"properties_to_select": ["server_id", "server_name"]}),
            ("output type given", {"output_type": "TO_LIST"}),
            ("group by given", {"group_by": "server_name"}),
            ("sort by given", {"sort_by": ["server_name", "server_id"]}),
        ]
    )
    def test_from_kwargs(self, _, mock_kwargs):
        """
        tests that from_kwargs static method works expectedly
        method should create a QueryOutputDetails with default params
        """
        out = self.instance.from_kwargs(prop_cls=ServerProperties, **mock_kwargs)
        if "properties_to_select" not in mock_kwargs.keys():
            self.assertEqual(out.properties_to_select, list(ServerProperties))
        else:
            self.assertEqual(
                out.properties_to_select,
                [ServerProperties.SERVER_ID, ServerProperties.SERVER_NAME],
            )

        if "output_type" not in mock_kwargs.keys():
            self.assertEqual(out.output_type, QueryOutputTypes.TO_STR)
        else:
            self.assertEqual(out.output_type, QueryOutputTypes.TO_LIST)

        if "group_by" not in mock_kwargs.keys():
            self.assertEqual(out.group_by, None)
        else:
            self.assertEqual(out.group_by, ServerProperties.SERVER_NAME)

        if "sort_by" not in mock_kwargs.keys():
            self.assertEqual(out.sort_by, None)
        else:
            self.assertEqual(
                out.sort_by,
                [
                    (ServerProperties.SERVER_NAME, False),
                    (ServerProperties.SERVER_ID, False),
                ],
            )

        self.assertEqual(out.group_ranges, None)
        self.assertEqual(out.include_ungrouped_results, False)
