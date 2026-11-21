import pytest

from apis.utils.sort_utils import sort_dictionaries


def test_sort_ascending():
    """Test sorting dictionaries in ascending order by default."""
    data = [{"age": 30}, {"age": 20}, {"age": 40}]

    result = sort_dictionaries(data, "age")

    assert result == [{"age": 20}, {"age": 30}, {"age": 40}]


def test_sort_descending():
    """Test sorting dictionaries in descending order."""
    data = [{"age": 30}, {"age": 20}, {"age": 40}]

    result = sort_dictionaries(data, "age", reverse=True)

    assert result == [{"age": 40}, {"age": 30}, {"age": 20}]


def test_sort_strings():
    """Test sorting dictionaries by string values."""
    data = [{"name": "Charlie"}, {"name": "Alice"}, {"name": "Bob"}]

    result = sort_dictionaries(data, "name")

    assert result == [
        {"name": "Alice"},
        {"name": "Bob"},
        {"name": "Charlie"},
    ]


def test_sort_duplicate_values():
    """Test that sorting preserves the order of equal values."""
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 20},
        {"name": "Charlie", "age": 30},
    ]

    result = sort_dictionaries(data, "age")

    assert result == [
        {"name": "Bob", "age": 20},
        {"name": "Alice", "age": 30},
        {"name": "Charlie", "age": 30},
    ]


def test_sort_empty_list():
    """Test that sorting an empty list returns an empty list."""
    assert sort_dictionaries([], "age") == []


def test_sort_single_dictionary():
    """Test that sorting a single dictionary returns the same content."""
    data = [{"age": 30}]

    assert sort_dictionaries(data, "age") == data


def test_sort_missing_key():
    """Test that a missing key raises KeyError with the expected message."""
    data = [{"age": 30}, {"name": "Alice"}]

    with pytest.raises(
        KeyError,
        match="Key 'age' not found in dictionary",
    ):
        sort_dictionaries(data, "age")


def test_sort_missing_key_in_all_dictionaries():
    """Test that KeyError is raised when no dictionary contains the key."""
    data = [{"name": "Alice"}, {"name": "Bob"}]

    with pytest.raises(KeyError):
        sort_dictionaries(data, "age")


def test_sort_negative_numbers():
    """Test sorting dictionaries containing negative numbers."""
    data = [{"value": -5}, {"value": 10}, {"value": -20}]

    result = sort_dictionaries(data, "value")

    assert result == [{"value": -20}, {"value": -5}, {"value": 10}]


def test_sort_float_values():
    """Test sorting dictionaries containing floating-point values."""
    data = [{"value": 2.5}, {"value": 1.1}, {"value": 3.7}]

    result = sort_dictionaries(data, "value")

    assert result == [{"value": 1.1}, {"value": 2.5}, {"value": 3.7}]


def test_sort_does_not_modify_original():
    """Test that sorting does not modify the original list."""
    data = [{"age": 30}, {"age": 20}, {"age": 40}]
    original = [item.copy() for item in data]

    result = sort_dictionaries(data, "age")

    assert data == original
    assert result is not data


def test_sort_explicit_reverse_false():
    """Test that reverse=False explicitly sorts in ascending order."""
    data = [{"age": 30}, {"age": 10}, {"age": 20}]

    result = sort_dictionaries(data, "age", reverse=False)

    assert result == [{"age": 10}, {"age": 20}, {"age": 30}]


@pytest.mark.parametrize(
    "data, key, reverse, expected",
    [
        (
            [{"x": 3}, {"x": 1}, {"x": 2}],
            "x",
            False,
            [{"x": 1}, {"x": 2}, {"x": 3}],
        ),
        (
            [{"x": 3}, {"x": 1}, {"x": 2}],
            "x",
            True,
            [{"x": 3}, {"x": 2}, {"x": 1}],
        ),
        (
            [{"x": 1}, {"x": 1}],
            "x",
            False,
            [{"x": 1}, {"x": 1}],
        ),
        (
            [],
            "x",
            False,
            [],
        ),
    ],
)
def test_sort_parametrized(data, key, reverse, expected):
    """Test multiple sorting scenarios using parametrized inputs."""
    assert sort_dictionaries(data, key, reverse) == expected
