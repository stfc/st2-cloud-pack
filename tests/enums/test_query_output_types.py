import pytest

from enums.query.query_output_types import QueryOutputTypes
from exceptions.parse_query_error import ParseQueryError


@pytest.mark.parametrize("output_type", ["to_HTML", "To_HtMl", "to_html"])
def test_to_html_serialization(output_type):
    """
    Tests that variants of TO_HTML can be serialized
    """
    assert QueryOutputTypes.from_string(output_type) is QueryOutputTypes.TO_HTML


@pytest.mark.parametrize(
    "output_type", ["to_OBJECT_LIST", "To_ObJecT_LisT", "to_object_list"]
)
def test_to_object_list_serialization(output_type):
    """
    Tests that variants of TO_OBJECT_LIST can be serialized
    """
    assert QueryOutputTypes.from_string(output_type) is QueryOutputTypes.TO_OBJECT_LIST


@pytest.mark.parametrize("output_type", ["to_LIST", "To_LiSt", "to_list"])
def test_to_list_serialization(output_type):
    """
    Tests that variants of TO_LIST can be serialized
    """
    assert QueryOutputTypes.from_string(output_type) is QueryOutputTypes.TO_LIST


@pytest.mark.parametrize("output_type", ["to_Str", "To_StR", "to_str"])
def test_to_str_serialization(output_type):
    """
    Tests that variants of TO_STR can be serialized
    """
    assert QueryOutputTypes.from_string(output_type) is QueryOutputTypes.TO_STR


def test_invalid_serialization():
    """
    Tests that error is raised when passes invalid string
    """
    with pytest.raises(ParseQueryError):
        QueryOutputTypes.from_string("some-invalid-string")
