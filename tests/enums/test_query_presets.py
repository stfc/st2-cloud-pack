import unittest
from parameterized import parameterized

from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsInteger,
    QueryPresetsString,
    QueryPresetsDateTime,
)
from exceptions.parse_query_error import ParseQueryError


class QueryPresetsTests(unittest.TestCase):
    @parameterized.expand(
        [
            ("lowercase", "equal_to"),
            ("capitalized", "Equal_To"),
            ("mix_case", "EqUaL_tO"),
        ]
    )
    def test_equal_to_serialization(self, _, val):
        """
        Tests that variants of EQUAL_TO can be serialized
        """
        assert QueryPresetsGeneric.from_string(val) is QueryPresetsGeneric.EQUAL_TO

    @parameterized.expand(
        [
            ("lowercase", "not_equal_to"),
            ("capitalized", "Not_Equal_To"),
            ("mix_case", "NoT_EqUaL_tO"),
        ]
    )
    def test_not_equal_to_serialization(self, _, val):
        """
        Tests that variants of NOT_EQUAL_TO can be serialized
        """
        assert QueryPresetsGeneric.from_string(val) is QueryPresetsGeneric.NOT_EQUAL_TO

    @parameterized.expand(
        [
            ("lowercase", "greater_than"),
            ("capitalized", "Greater_Than"),
            ("mix_case", "GrEaTer_ThAn"),
        ]
    )
    def test_greater_than_serialization(self, _, val):
        """
        Tests that variants of GREATER_THAN can be serialized
        """
        assert QueryPresetsInteger.from_string(val) is QueryPresetsInteger.GREATER_THAN

    @parameterized.expand(
        [
            ("lowercase", "greater_than_or_equal_to"),
            ("capitalized", "Greater_Than_Or_Equal_To"),
            ("mix_case", "GrEaTer_ThAn_Or_EqUaL_tO"),
        ]
    )
    def test_greater_than_or_equal_to_serialization(self, _, val):
        """
        Tests that variants of GREATER_THAN_OR_EQUAL_TO can be serialized
        """
        assert (
            QueryPresetsInteger.from_string(val)
            is QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO
        )

    @parameterized.expand(
        [
            ("lowercase", "less_than"),
            ("capitalized", "Less_Than"),
            ("mix_case", "LeSs_ThAn"),
        ]
    )
    def test_less_than_serialization(self, _, val):
        """
        Tests that variants of LESS_THAN can be serialized
        """
        assert QueryPresetsInteger.from_string(val) is QueryPresetsInteger.LESS_THAN

    @parameterized.expand(
        [
            ("lowercase", "less_than_or_equal_to"),
            ("capitalized", "Less_Than_Or_Equal_To"),
            ("mix_case", "LeSs_ThAn_Or_EqUaL_tO"),
        ]
    )
    def test_less_than_or_equal_to_serialization(self, _, val):
        """
        Tests that variants of LESS_THAN_OR_EQUAL_TO can be serialized
        """
        assert (
            QueryPresetsInteger.from_string(val)
            is QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO
        )

    @parameterized.expand(
        [
            ("lowercase", "older_than"),
            ("capitalized", "Older_Than"),
            ("mix_case", "OlDeR_ThAn"),
        ]
    )
    def test_older_than_serialization(self, _, val):
        """
        Tests that variants of OLDER_THAN can be serialized
        """
        assert QueryPresetsDateTime.from_string(val) is QueryPresetsDateTime.OLDER_THAN

    @parameterized.expand(
        [
            ("lowercase", "older_than_or_equal_to"),
            ("capitalized", "Older_Than_Or_Equal_To"),
            ("mix_case", "OlDeR_ThAn_Or_EqUaL_To"),
        ]
    )
    def test_older_than_or_equal_to_serialization(self, _, val):
        """
        Tests that variants of OLDER_THAN_OR_EQUAL_TO can be serialized
        """
        assert (
            QueryPresetsDateTime.from_string(val)
            is QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO
        )

    @parameterized.expand(
        [
            ("lowercase", "younger_than"),
            ("capitalized", "Younger_Than"),
            ("mix_case", "YoUnGeR_ThAn"),
        ]
    )
    def test_younger_than_serialization(self, _, val):
        """
        Tests that variants of YOUNGER_THAN can be serialized
        """
        assert (
            QueryPresetsDateTime.from_string(val) is QueryPresetsDateTime.YOUNGER_THAN
        )

    @parameterized.expand(
        [
            ("lowercase", "younger_than_or_equal_to"),
            ("capitalized", "Younger_Than_Or_Equal_To"),
            ("mix_case", "YoUngEr_ThAn_Or_EqUaL_To"),
        ]
    )
    def test_older_than_or_equal_to_serialization(self, _, val):
        """
        Tests that variants of YOUNGER_THAN_OR_EQUAL_TO can be serialized
        """
        assert (
            QueryPresetsDateTime.from_string(val)
            is QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO
        )

    @parameterized.expand(
        [("lowercase", "any_in"), ("capitalized", "Any_In"), ("mix_case", "AnY_In")]
    )
    def test_any_in_serialization(self, _, val):
        """
        Tests that variants of ANY_IN can be serialized
        """
        assert QueryPresetsString.from_string(val) is QueryPresetsString.ANY_IN

    @parameterized.expand(
        [
            ("lowercase", "not_any_in"),
            ("capitalized", "Not_Any_In"),
            ("mix_case", "NoT_AnY_In"),
        ]
    )
    def test_any_in_serialization(self, _, val):
        """
        Tests that variants of NOT_ANY_IN can be serialized
        """
        assert QueryPresetsString.from_string(val) is QueryPresetsString.NOT_ANY_IN

    @parameterized.expand(
        [
            ("lowercase", "matches_regex"),
            ("capitalized", "Matches_Regex"),
            ("mix_case", "MaTcHeS_ReGeX"),
        ]
    )
    def test_any_in_serialization(self, _, val):
        """
        Tests that variants of MATCHES_REGEX can be serialized
        """
        assert QueryPresetsString.from_string(val) is QueryPresetsString.MATCHES_REGEX

    def test_invalid_serialization(self):
        """
        Tests that error is raised when passes invalid string to all preset classes
        """
        for enum_cls in [
            QueryPresetsInteger,
            QueryPresetsString,
            QueryPresetsDateTime,
            QueryPresetsGeneric,
        ]:
            with self.assertRaises(ParseQueryError):
                enum_cls.from_string("some-invalid-string")
