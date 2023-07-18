import unittest
from unittest.mock import MagicMock

from structs.query.query_output_details import QueryOutputDetails

from tests.lib.openstack_query.mocks.mocked_props import MockProperties
from tests.lib.openstack_query.mocks.mocked_structs import MOCKED_OUTPUT_DETAILS


class QueryOutputDetailsTests(unittest.TestCase):
    """
    This class tests that helper functions in the QueryOutputDetails
    """

    def setUp(self) -> None:
        self.instance = QueryOutputDetails

    def test_from_kwargs(self):
        """
        tests that from_kwargs static method works expectedly
        should iteratively convert properties into given enums class and output_type into output type enum.
        set correct attributes in QueryOutputDetails dataclass and return
        """

        mock_prop_cls = MagicMock()
        mock_prop_cls.from_string.side_effect = [
            (MockProperties.PROP_1),
            (MockProperties.PROP_2),
        ]

        res = QueryOutputDetails.from_kwargs(
            prop_cls=mock_prop_cls,
            properties_to_select=["prop1", "prop2"],
            output_type="to_str",
        )
        self.assertEqual(res, MOCKED_OUTPUT_DETAILS)
