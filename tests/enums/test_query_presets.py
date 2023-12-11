import pytest

from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsInteger,
    QueryPresetsString,
    QueryPresetsDateTime,
    get_preset_from_string,
)
from exceptions.parse_query_error import ParseQueryError


@pytest.mark.parametrize(
    "preset_string", ["equal_to", "Equal_To", "EqUaL_tO", "equal", "=="]
)
def test_equal_to_serialization(preset_string):
    """
    Tests that variants of EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsGeneric.from_string(preset_string) is QueryPresetsGeneric.EQUAL_TO
    )


@pytest.mark.parametrize(
    "preset_string", ["not_equal_to", "Not_Equal_To", "NoT_EqUaL_tO", "not_equal", "!="]
)
def test_not_equal_to_serialization(preset_string):
    """
    Tests that variants of NOT_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsGeneric.from_string(preset_string)
        is QueryPresetsGeneric.NOT_EQUAL_TO
    )


@pytest.mark.parametrize(
    "preset_string", ["greater_than", "Greater_Than", "GrEaTer_ThAn"]
)
def test_greater_than_serialization(preset_string):
    """
    Tests that variants of GREATER_THAN can be serialized
    """
    assert (
        QueryPresetsInteger.from_string(preset_string)
        is QueryPresetsInteger.GREATER_THAN
    )


@pytest.mark.parametrize(
    "preset_string",
    [
        "greater_than_or_equal_to",
        "Greater_Than_Or_Equal_To",
        "GrEaTer_ThAn_Or_EqUaL_tO",
    ],
)
def test_greater_than_or_equal_to_serialization(preset_string):
    """
    Tests that variants of GREATER_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsInteger.from_string(preset_string)
        is QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO
    )


@pytest.mark.parametrize("preset_string", ["less_than", "Less_Than", "LeSs_ThAn"])
def test_less_than_serialization(preset_string):
    """
    Tests that variants of LESS_THAN can be serialized
    """
    assert (
        QueryPresetsInteger.from_string(preset_string) is QueryPresetsInteger.LESS_THAN
    )


@pytest.mark.parametrize(
    "preset_string",
    ["less_than_or_equal_to", "Less_Than_Or_Equal_To", "LeSs_ThAn_Or_EqUaL_tO"],
)
def test_less_than_or_equal_to_serialization(preset_string):
    """
    Tests that variants of LESS_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsInteger.from_string(preset_string)
        is QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO
    )


@pytest.mark.parametrize("preset_string", ["older_than", "Older_Than", "OlDeR_ThAn"])
def test_older_than_serialization(preset_string):
    """
    Tests that variants of OLDER_THAN can be serialized
    """
    assert (
        QueryPresetsDateTime.from_string(preset_string)
        is QueryPresetsDateTime.OLDER_THAN
    )


@pytest.mark.parametrize(
    "preset_string",
    ["older_than_or_equal_to", "Older_Than_Or_Equal_To", "OlDeR_ThAn_Or_EqUaL_To"],
)
def test_older_than_or_equal_to_serialization(preset_string):
    """
    Tests that variants of OLDER_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsDateTime.from_string(preset_string)
        is QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO
    )


@pytest.mark.parametrize(
    "preset_string", ["younger_than", "Younger_Than", "YoUnGeR_ThAn"]
)
def test_younger_than_serialization(preset_string):
    """
    Tests that variants of YOUNGER_THAN can be serialized
    """
    assert (
        QueryPresetsDateTime.from_string(preset_string)
        is QueryPresetsDateTime.YOUNGER_THAN
    )


@pytest.mark.parametrize(
    "preset_string",
    [
        "younger_than_or_equal_to",
        "Younger_Than_Or_Equal_To",
        "YoUngEr_ThAn_Or_EqUaL_To",
    ],
)
def test_younger_than_or_equal_to_serialization(preset_string):
    """
    Tests that variants of YOUNGER_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsDateTime.from_string(preset_string)
        is QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO
    )


@pytest.mark.parametrize("preset_string", ["any_in", "Any_In", "AnY_In", "in"])
def test_any_in_serialization(preset_string):
    """
    Tests that variants of ANY_IN can be serialized
    """
    assert QueryPresetsGeneric.from_string(preset_string) is QueryPresetsGeneric.ANY_IN


@pytest.mark.parametrize(
    "preset_string", ["not_any_in", "Not_Any_In", "NoT_AnY_In", "not_in"]
)
def test_not_any_in_serialization(preset_string):
    """
    Tests that variants of NOT_ANY_IN can be serialized
    """
    assert (
        QueryPresetsGeneric.from_string(preset_string) is QueryPresetsGeneric.NOT_ANY_IN
    )


@pytest.mark.parametrize(
    "preset_string",
    ["matches_regex", "Matches_Regex", "MaTcHeS_ReGeX", "regex", "match_regex"],
)
def test_matches_regex_serialization(preset_string):
    """
    Tests that variants of MATCHES_REGEX can be serialized
    """
    assert (
        QueryPresetsString.from_string(preset_string)
        is QueryPresetsString.MATCHES_REGEX
    )


def test_invalid_serialization():
    """
    Tests that error is raised when passes invalid string to all preset classes
    """
    for enum_cls in [
        QueryPresetsInteger,
        QueryPresetsString,
        QueryPresetsDateTime,
        QueryPresetsGeneric,
    ]:
        with pytest.raises(ParseQueryError):
            enum_cls.from_string("some-invalid-string")


@pytest.mark.parametrize(
    "alias, expected_preset",
    [
        ("equal_to", QueryPresetsGeneric.EQUAL_TO),
        ("matches_regex", QueryPresetsString.MATCHES_REGEX),
        ("older_than", QueryPresetsDateTime.OLDER_THAN),
        ("greater_than", QueryPresetsInteger.GREATER_THAN),
    ],
)
def test_get_preset_from_string_valid(alias, expected_preset):
    """
    Tests that get_preset_from_string works for a valid preset alias from each preset type
    """
    assert get_preset_from_string(alias) == expected_preset


def test_get_preset_from_string_invalid():
    """
    Tests that get_preset_from_string returns error if given an invalid alias
    """
    with pytest.raises(ParseQueryError):
        get_preset_from_string("invalid-alias")
