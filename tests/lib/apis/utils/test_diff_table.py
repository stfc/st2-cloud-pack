from unittest.mock import patch
import pytest

from apis.utils.diff_table import diff_to_tabulate_table


@pytest.fixture(name="mock_object1")
def mock_object1_fixture():
    return {
        "id": 1,
        "metadata": {"cores": 6, "disk": 50},
        "tags": ["tag3"],
        "name": "test1",
    }


@pytest.fixture(name="mock_object2")
def mock_object2_fixture():
    return {
        "id": 2,
        "metadata": {"cores": 4, "gpus": 10},
        "tags": ["tag1", "tag2"],
        "name": 123,
    }


def test_diff(mock_object1, mock_object2):
    with patch("deepdiff.DeepDiff") as mock_deepdiff:
        diff_to_tabulate_table(mock_object1, mock_object2)
        mock_deepdiff.assert_called_once_with(
            t1=mock_object1,
            t2=mock_object2,
            exclude_paths=None,
            threshold_to_diff_deeper=0,
            ignore_order=True,
        )


def test_diff_with_exclude_paths(mock_object1, mock_object2):
    with patch("deepdiff.DeepDiff") as mock_deepdiff:
        diff_to_tabulate_table(mock_object1, mock_object2, ["root['id']"])
        mock_deepdiff.assert_called_once_with(
            t1=mock_object1,
            t2=mock_object2,
            exclude_paths=["root['id']"],
            threshold_to_diff_deeper=0,
            ignore_order=True,
        )


def test_no_diff(mock_object1, mock_object2):
    with patch("deepdiff.DeepDiff") as mock_deepdiff:
        mock_deepdiff.return_value = {}
        res = diff_to_tabulate_table(mock_object1, mock_object2)
        mock_deepdiff.assert_called_once_with(
            t1=mock_object1,
            t2=mock_object2,
            exclude_paths=None,
            threshold_to_diff_deeper=0,
            ignore_order=True,
        )
    assert not res


def test_diff_with_values_changed(mock_object1, mock_object2):
    with patch("deepdiff.DeepDiff") as mock_deepdiff:
        mock_deepdiff.return_value = {
            "values_changed": {"root['id']": {"new_value": 2, "old_value": 1}}
        }
        res = diff_to_tabulate_table(mock_object1, mock_object2)
        mock_deepdiff.assert_called_once_with(
            t1=mock_object1,
            t2=mock_object2,
            exclude_paths=None,
            threshold_to_diff_deeper=0,
            ignore_order=True,
        )
    assert res == [["root['id']", 1, 2]]


def test_diff_with_dictionary_item_added(mock_object1, mock_object2):
    with patch("deepdiff.DeepDiff") as mock_deepdiff:
        mock_deepdiff.return_value = {
            "dictionary_item_added": ["root['metadata']['gpus']"]
        }
        res = diff_to_tabulate_table(mock_object1, mock_object2)
        mock_deepdiff.assert_called_once_with(
            t1=mock_object1,
            t2=mock_object2,
            exclude_paths=None,
            threshold_to_diff_deeper=0,
            ignore_order=True,
        )
    assert res == [["root['metadata']['gpus']", "Not Present", 10]]


def test_diff_with_dictionary_item_removed(mock_object1, mock_object2):
    with patch("deepdiff.DeepDiff") as mock_deepdiff:
        mock_deepdiff.return_value = {
            "dictionary_item_removed": ["root['metadata']['disk']"]
        }
        res = diff_to_tabulate_table(mock_object1, mock_object2)
        mock_deepdiff.assert_called_once_with(
            t1=mock_object1,
            t2=mock_object2,
            exclude_paths=None,
            threshold_to_diff_deeper=0,
            ignore_order=True,
        )
    assert res == [["root['metadata']['disk']", 50, "Not Present"]]


def test_diff_with_iterable_item_added(mock_object1, mock_object2):
    with patch("deepdiff.DeepDiff") as mock_deepdiff:
        mock_deepdiff.return_value = {
            "iterable_item_added": {"root['tags'][1]": "tag2"}
        }
        res = diff_to_tabulate_table(mock_object1, mock_object2)
        mock_deepdiff.assert_called_once_with(
            t1=mock_object1,
            t2=mock_object2,
            exclude_paths=None,
            threshold_to_diff_deeper=0,
            ignore_order=True,
        )
    assert res == [["root['tags'][1]", "N/A", "tag2"]]


def test_diff_with_iterable_item_removed(mock_object1, mock_object2):
    with patch("deepdiff.DeepDiff") as mock_deepdiff:
        mock_deepdiff.return_value = {
            "iterable_item_removed": {"root['tags'][1]": "tag2"}
        }
        res = diff_to_tabulate_table(mock_object1, mock_object2)
        mock_deepdiff.assert_called_once_with(
            t1=mock_object1,
            t2=mock_object2,
            exclude_paths=None,
            threshold_to_diff_deeper=0,
            ignore_order=True,
        )
    assert res == [["root['tags'][1]", "tag2", "N/A"]]


def test_diff_with_type_changes(mock_object1, mock_object2):
    with patch("deepdiff.DeepDiff") as mock_deepdiff:
        mock_deepdiff.return_value = {
            "type_changes": {
                "root['name']": {
                    "old_type": str,
                    "new_type": int,
                    "old_value": "test1",
                    "new_value": 123,
                }
            }
        }
        res = diff_to_tabulate_table(mock_object1, mock_object2)
        mock_deepdiff.assert_called_once_with(
            t1=mock_object1,
            t2=mock_object2,
            exclude_paths=None,
            threshold_to_diff_deeper=0,
            ignore_order=True,
        )
    assert res == [["root['name']", "'test1' (Type: str)", "'123' (Type: int)"]]
