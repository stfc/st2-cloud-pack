import pytest
from apis.utils.diff_utils import DiffUtils, _format_value, _normalize_path, get_diff

# pylint:disable=protected-access


# -------------------- format_value --------------------
@pytest.mark.parametrize(
    "value, expected",
    [
        (None, "None"),
        ("abc", "'abc'"),
        (123, "123"),
        (1.23, "1.23"),
        (True, "True"),
    ],
)
def test_format_value_simple(value, expected):
    """Test that _format_value correctly formats simple primitive types."""
    assert _format_value(value) == expected


def test_format_value_complex_object():
    """Test that _format_value truncates and labels complex object string representations."""

    class Dummy:  # pylint: disable=too-few-public-methods
        def __str__(self):
            return "X" * 100

    v = Dummy()
    result = _format_value(v)
    assert result.startswith("Dummy:")
    assert result.endswith("...")  # truncated


# -------------------- normalize_path --------------------


@pytest.mark.parametrize(
    "inp, expected",
    [
        ("root['a'][0]", "root/a/0"),
        ("root['x']['y']", "root/x/y"),
        ("root[0]", "root/0"),
    ],
)
def test_normalize_path(inp, expected):
    """Test that _normalize_path converts bracket notation into slash-separated format."""
    assert _normalize_path(inp) == expected


# -------------------- is_excluded --------------------


def test_is_excluded_true_and_false():
    """Test that excluded paths are correctly matched or ignored."""
    du = DiffUtils(exclude_paths={"root['a'][*]", "root['x']"})
    assert du._is_excluded("root['a'][0]") is True
    assert du._is_excluded("root['b']") is False


# -------------------- _get_diff_dict --------------------


def test_get_diff_dict_add_remove_and_queue():
    """Test that dict differences are reported for missing keys in source and target."""
    du = DiffUtils()
    src = {"a": 1}
    tgt = {"b": 2}
    du._get_diff_dict(src, tgt, "root")

    assert ["root['b']", "Not Present", "2"] in du.changes
    assert ["root['a']", "1", "Not Present"] in du.changes


def test_get_diff_dict_queue_added():
    """Test that differing dict values are queued for deeper comparison instead of reported immediately."""
    du = DiffUtils()
    src = {"a": 1}
    tgt = {"a": 2}
    du._get_diff_dict(src, tgt, "root")

    assert du.queue  # queued, not directly added to changes


def test_get_diff_dict_with_excluded():
    """Test that excluded dict keys are skipped and produce no changes."""
    du = DiffUtils(exclude_paths={"root['x']"})
    du._get_diff_dict({"x": 1}, {"x": 2}, "root")
    assert not du.changes
    assert not du.queue


# -------------------- _get_diff_list_hashable --------------------


def test_get_diff_list_hashable_changes():
    """Test that hashable list elements are diffed using counts and reported correctly."""
    du = DiffUtils()
    du._get_diff_list_hashable([1, 2], [2, 3], "root")
    assert ["root[?]", "1", "Not Present"] in du.changes
    assert ["root[?]", "Not Present", "3"] in du.changes


# -------------------- _get_diff_list_unhashable --------------------


def test_get_diff_list_unhashable_perfect_match():
    """Test that identical unhashable list items (dicts) produce no changes."""
    du = DiffUtils()
    du._get_diff_list_unhashable([{"a": 1}], [{"a": 1}], "root")
    assert du.changes == []


def test_get_diff_list_unhashable_close_match():
    """Test that unhashable list items with nested diffs report sub-changes."""
    du = DiffUtils()
    du._get_diff_list_unhashable([{"a": 1}], [{"a": 2}], "root")
    assert any("root[?]" in c[0] for c in du.changes)


def test_get_diff_list_unhashable_unmatched_source_and_target():
    """Test that unmatched unhashable items are reported as missing in source or target."""
    du = DiffUtils()
    du._get_diff_list_unhashable([{"a": 1}], [], "root")
    assert ["root[?]", "dict: {'a': 1}...", "Not Present"] in du.changes

    du2 = DiffUtils()
    du2._get_diff_list_unhashable([], [{"a": 2}], "root")
    assert ["root[?]", "Not Present", "dict: {'a': 2}..."] in du2.changes


def test_get_diff_list_unhashable_second_pass_skip():
    """Test that unhashable list diff second-pass correctly reports extra unmatched targets."""
    du = DiffUtils()
    du._get_diff_list_unhashable([{"a": 1}], [{"a": 2}, {"b": 3}], "root")
    assert any("Not Present" in c for c in du.changes)


def test_get_diff_list_unhashable_skips_already_matched():
    """Test that once a target item is matched, later passes skip it (if not matched_in_tgt[j] == False)."""
    du = DiffUtils()
    src = [{"a": 1}, {"a": 1}]
    tgt = [{"a": 1}]
    du._get_diff_list_unhashable(src, tgt, "root")

    assert ["root[?]", "dict: {'a': 1}...", "Not Present"] in du.changes


# -------------------- _get_diff_list_unordered --------------------


def test_get_diff_list_unordered_mixed():
    """Test that unordered list diff detects differences for hashable and dict items."""
    du = DiffUtils()
    du._get_diff_list_unordered([1, {"a": 1}], [2, {"a": 2}], "root")
    assert any("Not Present" in c for c in du.changes)


# -------------------- _get_diff_list_ordered --------------------


def test_get_diff_list_ordered_extra_in_target_and_source():
    """Test that ordered list diff reports extra elements in either source or target."""
    du = DiffUtils()
    du._get_diff_list_ordered([1], [1, 2], "root")
    assert ["root[1]", "Not Present", "2"] in du.changes

    du2 = DiffUtils()
    du2._get_diff_list_ordered([1, 2], [1], "root")
    assert ["root[1]", "2", "Not Present"] in du2.changes


def test_get_diff_list_ordered_queue():
    """Test that differing elements in ordered lists are queued for deeper comparison."""
    du = DiffUtils()
    du._get_diff_list_ordered([1], [2], "root")
    assert (1, 2, "root[0]") in du.queue


# -------------------- _get_diff_set --------------------


def test_get_diff_set_changes():
    """Test that set differences report missing elements on each side."""
    du = DiffUtils()
    du._get_diff_set({1}, {2}, "root")
    assert ["root", "1", "Not Present in Set"] in du.changes
    assert ["root", "Not Present in Set", "2"] in du.changes


# -------------------- get_diff --------------------


def test_get_diff_type_mismatch():
    """Test that type mismatches are reported as differences."""
    changes = get_diff(1, "1")
    assert ["root", "1", "'1'"] in changes


def test_get_diff_dict_and_list_and_set():
    """Test that nested dicts, lists, and sets produce appropriate differences."""
    obj1 = {"a": [1, 2], "b": {1, 2}}
    obj2 = {"a": [2, 3], "b": {2, 3}}
    changes = get_diff(obj1, obj2)
    assert any("Not Present" in c for c in changes)


def test_get_diff_ignore_order_false():
    """Test that list order is respected when ignore_order=False."""
    obj1 = [1, 2]
    obj2 = [2, 1]
    changes = get_diff(obj1, obj2, ignore_order=False)
    assert changes  # differences expected


def test_get_diff_with_excluded_path():
    """Test that excluded paths are skipped in the top-level diff."""
    obj1 = {"x": 1}
    obj2 = {"x": 2}
    changes = get_diff(obj1, obj2, exclude_paths={"root['x']"})
    assert not changes


def test_get_diff_circular_reference():
    """Test that circular references do not cause infinite recursion."""
    a, b = {}, {}
    a["self"] = a
    b["self"] = b
    changes = get_diff(a, b)
    assert changes == []


def test_get_diff_root_excluded_skips_completely():
    """Test that excluding the root path skips comparison entirely."""
    obj1 = {"a": 1}
    obj2 = {"a": 2}
    changes = get_diff(obj1, obj2, exclude_paths={"root"})
    assert changes == []
