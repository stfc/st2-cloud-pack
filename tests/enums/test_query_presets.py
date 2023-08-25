import unittest

import pytest

from enums.query.query_presets import (
    QueryPresetsGeneric,
    QueryPresetsInteger,
    QueryPresetsString,
    QueryPresetsDateTime,
)
from exceptions.parse_query_error import ParseQueryError


@pytest.mark.parametrize("val",
    [
         "equal_to",
         "Equal_To",
         "EqUaL_to",
    ]
)
def test_equal_to_serialization(val):
    """
    Tests that variants of EQUAL_TO can be serialized
    """
    assert QueryPresetsGeneric.from_string(val) is QueryPresetsGeneric.EQUAL_TO

@pytest.mark.parametrize("val",
    [
         "not_equal_to",
         "Not_Equal_To",
         "NoT_EqUaL_to",
    ]
)
def test_not_equal_to_serialization(val):
    """
    Tests that variants of NOT_EQUAL_TO can be serialized
    """
    assert QueryPresetsGeneric.from_string(val) is QueryPresetsGeneric.NOT_EQUAL_TO

@pytest.mark.parametrize("val",
    [
         "greater_than",
         "Greater_Than",
         "GrEaTer_Than",
    ]
)
def test_greater_than_serialization(val):
    """
    Tests that variants of GREATER_THAN can be serialized
    """
    assert QueryPresetsInteger.from_string(val) is QueryPresetsInteger.GREATER_THAN

@pytest.mark.parametrize("val",
    [
         "greater_than_or_equal_to",
         "Greater_Than_Or_Equal_To",
         "GrEaTer_ThAn_Or_EqUaL_to",
    ]
)
def test_greater_than_or_equal_to_serialization(val):
    """
    Tests that variants of GREATER_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsInteger.from_string(val)
        is QueryPresetsInteger.GREATER_THAN_OR_EQUAL_TO
    )

@pytest.mark.parametrize("val",
    [
         "less_than",
         "Less_Than",
         "LeSs_Than",
    ]
)
def test_less_than_serialization(val):
    """
    Tests that variants of LESS_THAN can be serialized
    """
    assert QueryPresetsInteger.from_string(val) is QueryPresetsInteger.LESS_THAN

@pytest.mark.parametrize("val",
    [
         "less_than_or_equal_to",
         "Less_Than_Or_Equal_To",
         "LeSs_ThAn_Or_EqUaL_to",
    ]
)
def test_less_than_or_equal_to_serialization(val):
    """
    Tests that variants of LESS_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsInteger.from_string(val)
        is QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO
    )

@pytest.mark.parametrize("val",
    [
         "older_than",
         "Older_Than",
         "OlDeR_Than",
    ]
)
def test_older_than_serialization(val):
    """
    Tests that variants of OLDER_THAN can be serialized
    """
    assert QueryPresetsDateTime.from_string(val) is QueryPresetsDateTime.OLDER_THAN

@pytest.mark.parametrize("val",
    [
         "older_than_or_equal_to",
         "Older_Than_Or_Equal_To",
         "OlDeR_ThAn_Or_EqUaL_To",
    ]
)
def test_older_than_or_equal_to_serialization(val):
    """
    Tests that variants of OLDER_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsDateTime.from_string(val)
        is QueryPresetsDateTime.OLDER_THAN_OR_EQUAL_TO
    )

@pytest.mark.parametrize("val",
    [
         "younger_than",
         "Younger_Than",
         "YoUnGeR_Than",
    ]
)
def test_younger_than_serialization(val):
    """
    Tests that variants of YOUNGER_THAN can be serialized
    """
    assert (
        QueryPresetsDateTime.from_string(val) is QueryPresetsDateTime.YOUNGER_THAN
    )

@pytest.mark.parametrize("val",
    [
         "younger_than_or_equal_to",
         "Younger_Than_Or_Equal_To",
         "YoUngEr_ThAn_Or_EqUaL_To",
    ]
)
def test_younger_than_or_equal_to_serialization(val):
    """
    Tests that variants of YOUNGER_THAN_OR_EQUAL_TO can be serialized
    """
    assert (
        QueryPresetsDateTime.from_string(val)
        is QueryPresetsDateTime.YOUNGER_THAN_OR_EQUAL_TO
    )

@pytest.mark.parametrize("val",
    ["any_in",  "Any_In",  "AnY_In"]
)
def test_any_in_serialization(val):
    """
    Tests that variants of ANY_IN can be serialized
    """
    assert QueryPresetsString.from_string(val) is QueryPresetsString.ANY_IN

@pytest.mark.parametrize("val",
    [
         "not_any_in",
         "Not_Any_In",
         "NoT_AnY_In",
    ]
)
def test_not_any_in_serialization(val):
    """
    Tests that variants of NOT_ANY_IN can be serialized
    """
    assert QueryPresetsString.from_string(val) is QueryPresetsString.NOT_ANY_IN

@pytest.mark.parametrize("val",
    [
         "matches_regex",
         "Matches_Regex",
         "MaTcHeS_Regex",
    ]
)
def test_matches_regex_serialization(val):
    """
    Tests that variants of MATCHES_REGEX can be serialized
    """
    assert QueryPresetsString.from_string(val) is QueryPresetsString.MATCHES_REGEX

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
