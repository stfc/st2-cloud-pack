from parameterized import parameterized

from enums.query.query_output_types import QueryOutputTypes


@parameterized(["to_HTML", "To_HtMl", "to_html"])
def test_to_html_serialization(val):
    """
    Tests that variants of TO_HTML can be serialized
    """
    assert QueryOutputTypes.from_string(val) is QueryOutputTypes.TO_HTML


@parameterized(["to_OBJECT_LIST", "To_ObJecT_LisT", "to_object_list"])
def test_to_object_list_serialization(val):
    """
    Tests that variants of TO_OBJECT_LIST can be serialized
    """
    assert QueryOutputTypes.from_string(val) is QueryOutputTypes.TO_OBJECT_LIST


@parameterized(["to_LIST", "To_LiSt", "to_list"])
def test_to_list_serialization(val):
    """
    Tests that variants of TO_LIST can be serialized
    """
    assert QueryOutputTypes.from_string(val) is QueryOutputTypes.TO_LIST


@parameterized(["to_Str", "To_StR", "to_str"])
def test_to_str_serialization(val):
    """
    Tests that variants of TO_STR can be serialized
    """
    assert QueryOutputTypes.from_string(val) is QueryOutputTypes.TO_STR
