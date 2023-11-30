import pytest

from enums.query.sort_order import SortOrder
from exceptions.parse_query_error import ParseQueryError


@pytest.mark.parametrize("sort_order_type", ["asc", "Asc", "Ascending"])
def test_asc_serialization(sort_order_type):
    """
    Tests that variants of ASC can be serialized
    """
    assert SortOrder.from_string(sort_order_type) is SortOrder.ASC


@pytest.mark.parametrize("sort_order_type", ["desc", "Desc", "Descending"])
def test_desc_serialization(sort_order_type):
    """
    Tests that variants of DESC can be serialized
    """
    assert SortOrder.from_string(sort_order_type) is SortOrder.DESC


def test_get_preset_from_string_invalid():
    """
    Tests that error is raised when passed invalid string
    """
    with pytest.raises(ParseQueryError):
        SortOrder.from_string("some-invalid-string")
