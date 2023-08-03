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
            ("no args use defaults", False, None),
            ("properties given, not output type", True, None),
            ("no properties given, output type given", False, "TO_OBJECT_LIST"),
            ("properties and output type given", True, "TO_LIST"),
        ]
    )
    def test_from_kwargs(self, _, set_mock_props, mock_output_type):
        """
        tests that from_kwargs static method works expectedly
        should iteratively convert properties into given enums class and output_type into output type enum.
        set correct attributes in QueryOutputDetails dataclass and return
        """

        expected_mock_props = list(ServerProperties)
        mock_props = [prop.name for prop in ServerProperties]
        if set_mock_props:
            expected_mock_props = [
                ServerProperties.SERVER_ID,
                ServerProperties.SERVER_NAME,
            ]
            mock_props = ["server_id", "server_name"]

        expected_mock_output_type = QueryOutputTypes.TO_STR
        if mock_output_type:
            expected_mock_output_type = QueryOutputTypes[mock_output_type]

        res = QueryOutputDetails.from_kwargs(
            prop_cls=ServerProperties,
            properties_to_select=mock_props,
            output_type=mock_output_type,
        )

        assert set(res.properties_to_select) == set(expected_mock_props)
        assert res.output_type == expected_mock_output_type
