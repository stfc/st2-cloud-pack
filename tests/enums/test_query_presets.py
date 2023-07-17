from parameterized import parameterized

from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsInteger,
    QueryPresetsString,
    QueryPresetsDateTime,
)


@parameterized(["equal_to", "Equal_To", "EqUaL_tO"])
def test_equal_to_serialization(val):
    """
    Tests that variants of EQUAL_TO can be serialized
    """
    assert QueryPresetsGeneric.from_string(val) is QueryPresetsGeneric.EQUAL_TO


@parameterized(["not_equal_to", "Not_Equal_To", "NoT_EqUaL_tO"])
def test_not_equal_to_serialization(val):
    """
    Tests that variants of NOT_EQUAL_TO can be serialized
    """
    assert QueryPresetsGeneric.from_string(val) is QueryPresetsGeneric.NOT_EQUAL_TO


@parameterized(["greater_than", "Greater_Than", "GrEaTer_ThAn"])
def test_greater_than_serialization(val):
    """
    Tests that variants of GREATER_THAN can be serialized
    """
    assert QueryPresetsInteger.from_string(val) is QueryPresetsInteger.GREATER_THAN


@parameterized(
    ["greater_than_or_equal_to", "Greater_Than_Or_Equal_To", "GrEaTer_ThAn_Or_EqUaL_tO"]
)
def test_greater_than_or_equal_to_serialization(val):
    """
    Tests that variants of GREATER_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsInteger.from_string(val)
        is QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO
    )


@parameterized(["less_than", "Less_Than", "LeSs_ThAn"])
def test_less_than_serialization(val):
    """
    Tests that variants of LESS_THAN can be serialized
    """
    assert QueryPresetsInteger.from_string(val) is QueryPresetsInteger.LESS_THAN


@parameterized(
    ["less_than_or_equal_to", "Less_Than_Or_Equal_To", "LeSs_ThAn_Or_EqUaL_tO"]
)
def test_less_than_or_equal_to_serialization(val):
    """
    Tests that variants of LESS_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsInteger.from_string(val)
        is QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO
    )


@parameterized(["older_than", "Older_Than", "OlDeR_ThAn"])
def test_older_than_serialization(val):
    """
    Tests that variants of OLDER_THAN can be serialized
    """
    assert QueryPresetsDateTime.from_string(val) is QueryPresetsDateTime.OLDER_THAN


@parameterized(
    ["older_than_or_equal_to", "Older_Than_Or_Equal_To", "OlDeR_ThAn_Or_EqUaL_To"]
)
def test_older_than_or_equal_to_serialization(val):
    """
    Tests that variants of OLDER_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsDateTime.from_string(val)
        is QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO
    )


@parameterized(["younger_than", "Younger_Than", "YoUnGeR_ThAn"])
def test_younger_than_serialization(val):
    """
    Tests that variants of YOUNGER_THAN can be serialized
    """
    assert QueryPresetsDateTime.from_string(val) is QueryPresetsDateTime.YOUNGER_THAN


@parameterized(
    ["younger_than_or_equal_to", "Younger_Than_Or_Equal_To", "YoUngEr_ThAn_Or_EqUaL_To"]
)
def test_older_than_or_equal_to_serialization(val):
    """
    Tests that variants of YOUNGER_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsDateTime.from_string(val)
        is QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO
    )


@parameterized(["any_in", "Any_In", "AnY_In"])
def test_any_in_serialization(val):
    """
    Tests that variants of ANY_IN can be serialized
    """
    assert QueryPresetsString.from_string(val) is QueryPresetsString.ANY_IN


@parameterized(["not_any_in", "Not_Any_In", "NoT_AnY_In"])
def test_any_in_serialization(val):
    """
    Tests that variants of NOT_ANY_IN can be serialized
    """
    assert QueryPresetsString.from_string(val) is QueryPresetsString.NOT_ANY_IN


@parameterized(["matches_regex", "Matches_Regex", "MaTcHeS_ReGeX"])
def test_any_in_serialization(val):
    """
    Tests that variants of MATCHES_REGEX can be serialized
    """
    assert QueryPresetsString.from_string(val) is QueryPresetsString.MATCHES_REGEX
